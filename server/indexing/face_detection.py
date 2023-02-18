import pathlib
import logging
from threading import Event, Thread

from PIL import Image
import torch
import numpy as np
import face_recognition

from server.db import async_client
from server.conf import (
    face_detection_workers_per_gpu,
    face_detection_max_width,
    face_detection_max_height,
    face_detection_batch_size,
    supported_image_types,
)
from server.indexing.utils import DataLoader
from server.utils import image_processing


LOG = logging.getLogger(__name__)
MAX_WIDTH = face_detection_max_width
MAX_HEIGHT = face_detection_max_height
BATCH_SIZE = face_detection_batch_size


def resize_bounding_boxes(faces, ratio):
    if ratio < 1:
        return [
            (
                int(top * (1 / ratio)),
                int(right * (1 / ratio)),
                int(bottom * (1 / ratio)),
                int(left * (1 / ratio)),
            )
            for (top, right, bottom, left) in faces
        ]
    return faces


def record_faces(entry, faces, encodings):
    async_client.ai_album.media.update_one(
        {"_id": entry["_id"]},
        {"$set": {"faces": faces, "faceEncodings": encodings}},
    )


def process_batch(batch_images, batch_entries, batch_ratios):
    face_count = 0
    batch_faces = face_recognition.batch_face_locations(batch_images, number_of_times_to_upsample=2, batch_size=face_detection_batch_size)

    for image, entry, ratio, faces in zip(
        batch_images, batch_entries, batch_ratios, batch_faces
    ):
        encodings = [
            enc.tolist()
            for enc in face_recognition.face_encodings(
                image, known_face_locations=faces, num_jitters=1, model="large"
            )
        ]
        faces = resize_bounding_boxes(faces, ratio)
        face_count += len(faces)
        record_faces(entry, faces, encodings)

    return face_count


class FaceDetectionWorker(Thread):
    def __init__(
        self,
        data_loader: DataLoader,
        worker_id: str,
        device_name: str | int,
        cuda: bool,
        task_dir: str,
        killer: Event,
    ):
        Thread.__init__(self)
        self.data_loader = data_loader
        self.worker_id = worker_id
        self.device_name = device_name
        self.task_dir = task_dir
        self.killer = killer
        self.processed = 0
        self.cuda = cuda

        if not self.cuda:
            self.batch = False
        else:
            self.batch = True

    def run(self) -> None:
        fetch = True
        LOG.debug(f"Starting face detection worker {self.worker_id}")

        while fetch and not self.killer.is_set():
            data = self.data_loader.get_next_batch()
            fetch = len(data) > 0
            batch_images = []
            batch_ratios = []
            batch_entries = []
            face_count = 0

            for entry in data:
                if self.killer.is_set():
                    break
                path = (
                    pathlib.Path()
                    .joinpath(self.task_dir, "data", entry["path"])
                    .as_posix()
                )

                image = Image.open(path).convert("RGB")
                image = image_processing.rotate_image(image)
                ratio = min(MAX_WIDTH / image.width, MAX_HEIGHT / image.height)

                if ratio < 1:
                    image = image.resize(
                        (round(image.width * ratio), round(image.height * ratio))
                    )
                image = image_processing.pad_image(image, MAX_WIDTH, MAX_HEIGHT)
                # image.show()
                image = np.array(image)

                if not self.batch:
                    faces = face_recognition.face_locations(image)
                    faces = faces = resize_bounding_boxes(faces, ratio)
                    record_faces(entry, faces)
                    self.processed += 1
                    LOG.debug(f"Detected {len(faces)} in image {image.shape}")
                else:
                    batch_images.append(image)
                    batch_ratios.append(ratio)
                    batch_entries.append(entry)

                if self.batch and len(batch_images) == BATCH_SIZE:
                    self.processed += BATCH_SIZE
                    face_count += process_batch(
                        batch_images, batch_entries, batch_ratios
                    )
                    batch_images = []
                    batch_ratios = []
                    batch_entries = []

            self.processed += len(batch_images)
            face_count += process_batch(batch_images, batch_entries, batch_ratios)
            batch_images = []
            batch_ratios = []
            batch_entries = []

            if self.batch:
                LOG.debug(f"Detected {face_count} faces in {BATCH_SIZE} images")

        LOG.debug(
            f"FACE_DETECTION_WORKER {self.worker_id} proceessed {self.processed} images. "
            + ("Exit by kill!" if self.killer.is_set() else "")
        )


def run_face_detection(task_dir, killer):
    device_count = torch.cuda.device_count()
    data_loader = DataLoader(
        async_client.ai_album.media,
        {
            "$and": [
                {"faces": {"$exists": False}},
                {
                    "path": {
                        "$regex": "|".join([f"{fmt}$" for fmt in supported_image_types])
                    }
                },
            ]
        },
        {"_id": 1, "path": 1},
        "name",
        BATCH_SIZE,
    )

    if data_loader.get_count() == 0:
        LOG.debug(f"Face detection not needed")
        return

    LOG.debug(f"Face detection needed for {data_loader.get_count()}.")

    if device_count > 0:
        workers = []
        for d in range(1):
            for w in range(face_detection_workers_per_gpu):
                workers.append(
                    FaceDetectionWorker(
                        data_loader, f"GPU{d}:WORKER{w}", d, True, task_dir, killer
                    )
                )
        LOG.debug(f"Running {len(workers)} face detection workers")
        [worker.start() for worker in workers]
        [worker.join() for worker in workers]
    else:
        LOG.debug("CUDA not found!")
        LOG.debug(f"Running 1 face detection worker")
        captioning_worker = FaceDetectionWorker(
            data_loader, "CPU:1", None, False, task_dir, killer
        )
        captioning_worker.start()
        captioning_worker.join()

    LOG.debug(f"Face detection complete")
