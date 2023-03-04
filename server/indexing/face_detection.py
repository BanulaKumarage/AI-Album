import pathlib
import logging
import gc
from threading import Event, Thread

from PIL import Image
import torch
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1

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


class BatchData:
    def __init__(self) -> None:
        self.images = []
        self.paths = []
        self.ratios = []
        self.entries = []

    def reset(self):
        self.images = []
        self.paths = []
        self.ratios = []
        self.entries = []

    def size(self):
        return len(self.images)


class FaceDetectionWorker(Thread):
    def __init__(
        self,
        data_loader: DataLoader,
        worker_id: str,
        device_name: str | int,
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
        self.mtcnn = MTCNN(
            select_largest=False,
            keep_all=True,
            post_process=False,
            device=self.device_name,
        )
        self.resnet = InceptionResnetV1(
            pretrained="vggface2", device=self.device_name
        ).eval()

    def record_faces(self, entry, faces, probs, encodings):
        async_client.ai_album.media.update_one(
            {"_id": entry["_id"]},
            {"$set": {"faces": faces, "probs": probs, "faceEncodings": encodings}},
        )

    def resize_bounding_boxes(self, faces, ratio):
        if ratio < 1:
            return [
                (
                    int(top * (1 / ratio)),
                    int(right * (1 / ratio)),
                    int(bottom * (1 / ratio)),
                    int(left * (1 / ratio)),
                )
                for (left, top, right, bottom) in faces
            ]
        return faces

    def process_batch(self, batch: BatchData):
        batch_images = batch.images
        batch_entries = batch.entries
        batch_ratios = batch.ratios
        batch_paths = batch.paths

        face_count = 0

        if len(batch_images) == 0:
            return 0

        with torch.no_grad():
            batch_faces, batch_probs = self.mtcnn.detect(batch_images)

        for path, entry, ratio, faces, probs in zip(
            batch_paths, batch_entries, batch_ratios, batch_faces, batch_probs
        ):
            if faces is not None:
                faces = faces.tolist()
                probs = probs.tolist()
                faces = [face for face, prob in zip(faces, probs) if prob > 0.9]
                probs = [prob for prob in probs if prob > 0.9]

                if not len(faces) == 0:
                    unscaled_image = Image.open(path).convert("RGB")
                    unscaled_face_boxes = [
                        [dim / max(1, ratio) for dim in face] for face in faces
                    ]

                    with torch.no_grad():
                        unscaled_faces = self.mtcnn.extract(
                            unscaled_image, unscaled_face_boxes, None
                        )
                        unscaled_faces = unscaled_faces.to(self.device_name)
                        encodings = self.resnet(unscaled_faces).cpu().tolist()

                    faces = self.resize_bounding_boxes(faces, ratio)
                    face_count += len(faces)
                    self.record_faces(entry, faces, probs, encodings)
                else:
                    self.record_faces(entry, [], [], [])
            else:
                self.record_faces(entry, [], [], [])

        return face_count

    def run(self) -> None:
        fetch = True
        LOG.debug(f"Starting face detection worker {self.worker_id}")

        while fetch and not self.killer.is_set():
            data = self.data_loader.get_next_batch()
            fetch = len(data) > 0
            batch = BatchData()
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
                batch.images.append(image)
                batch.ratios.append(ratio)
                batch.entries.append(entry)
                batch.paths.append(path)

                if batch.size() == BATCH_SIZE:
                    self.processed += BATCH_SIZE
                    face_count += self.process_batch(batch)
                    batch.reset()

            self.processed += batch.size()
            face_count += self.process_batch(batch)
            batch.reset()

            LOG.debug(f"Detected {face_count} faces in {BATCH_SIZE} images")

        del self.mtcnn
        del self.resnet

        with torch.no_grad():
            torch.cuda.empty_cache()

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
        for d in range(device_count):
            for w in range(face_detection_workers_per_gpu):
                workers.append(
                    FaceDetectionWorker(
                        data_loader,
                        f"GPU{d}:WORKER{w}",
                        f"cuda:{d}",
                        task_dir,
                        killer,
                    )
                )
        LOG.debug(f"Running {len(workers)} face detection workers")
        [worker.start() for worker in workers]
        [worker.join() for worker in workers]
    else:
        LOG.debug("CUDA not found!")
        LOG.debug(f"Running 1 face detection worker")
        captioning_worker = FaceDetectionWorker(
            data_loader, "CPU:1", "cpu", task_dir, killer
        )
        captioning_worker.start()
        captioning_worker.join()

    gc.collect()

    LOG.debug(
        f"CUDA memory after clanup allocated: {torch.cuda.memory_allocated()}, reserved {torch.cuda.memory_reserved()}"
    )

    LOG.debug(f"Face detection complete")
