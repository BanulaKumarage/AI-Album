import pathlib
import logging
import gc
from threading import Thread
from multiprocessing import Process, Event

from PIL import Image
import numpy as np
import tensorflow as tf
from deepface import DeepFace

from server.db import async_client
from server.conf import (
    face_detection_workers_per_device,
    face_detection_max_width,
    face_detection_max_height,
    face_detection_batch_size,
    supported_image_types,
)
from server.indexing.utils import DataLoader
from server.utils.image_processing import rotate_image


LOG = logging.getLogger(__name__)
MAX_WIDTH = face_detection_max_width
MAX_HEIGHT = face_detection_max_height
BATCH_SIZE = face_detection_batch_size


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

    def convert_face(self, face):
        x = face["x"]
        y = face["y"]
        h = face["h"]
        w = face["w"]

        return {"top": y, "left": x, "bottom": y + h, "right": x + w}

    def record_faces(self, entry, faces, probs, encodings):
        async_client.ai_album.media.update_one(
            {"_id": entry["_id"]},
            {
                "$set": {
                    "faces": [self.convert_face(face) for face in faces],
                    "probs": probs,
                    "faceEncodings": encodings,
                }
            },
        )

    def run(self) -> None:
        fetch = True
        LOG.debug(f"Starting face detection worker {self.worker_id}")

        while fetch and not self.killer.is_set():
            data = self.data_loader.get_next_batch()
            fetch = len(data) > 0
            faces_count = 0

            for entry in data:
                if self.killer.is_set():
                    break
                path = (
                    pathlib.Path()
                    .joinpath(self.task_dir, "data", entry["path"])
                    .as_posix()
                )

                image = np.array(rotate_image(Image.open(path)).convert("RGB"))
                

                with tf.device(self.device_name):
                    faces = DeepFace.represent(
                        np.array(image),
                        detector_backend="retinaface",
                        model_name="Facenet512",
                        enforce_detection=False,
                    )

                faces = [face for face in faces if face["face_confidence"] > 0.9]
                faces_count += len(faces)
                self.record_faces(
                    entry,
                    [face["facial_area"] for face in faces],
                    [face["face_confidence"] for face in faces],
                    [face["embedding"] for face in faces],
                )

            LOG.debug(f"{self.worker_id} Detected {faces_count} faces in {BATCH_SIZE} images")
            self.processed += faces_count

        LOG.debug(
            f"FACE_DETECTION_WORKER {self.worker_id} proceessed {self.processed} images. "
            + ("Exit by kill!" if self.killer.is_set() else "")
        )


def wrapper(task_dir, killer):
    devices = tf.config.get_visible_devices("GPU")
    device_count = len(devices)
    device_names = (
        [f"GPU:{g}" for g in range(device_count)] if device_count else ["CPU"]
    )

    if device_count:
        for device in devices:
            tf.config.experimental.set_memory_growth(device, True)

    data_loader = DataLoader(
        collection=async_client.ai_album.media,
        query={
            "$and": [
                {"faces": {"$exists": False}},
                {
                    "path": {
                        "$regex": "|".join([f"{fmt}$" for fmt in supported_image_types])
                    }
                },
            ]
        },
        projection={"_id": 1, "path": 1},
        sort="name",
        batch_size=BATCH_SIZE,
    )

    if data_loader.get_count() == 0:
        LOG.debug(f"Face detection not needed")
        return

    LOG.debug(f"Face detection needed for {data_loader.get_count()}.")
    workers = []

    for device in device_names:
        for worker in range(face_detection_workers_per_device):
            workers.append(
                FaceDetectionWorker(
                    data_loader=data_loader,
                    worker_id=f"{device}:WORKER{worker}",
                    device_name=device,
                    task_dir=task_dir,
                    killer=killer,
                )
            )
    LOG.debug(f"Running {len(workers)} face detection workers")
    [worker.start() for worker in workers]
    [worker.join() for worker in workers]

    gc.collect()

    LOG.debug(f"Face detection complete")


def run_face_detection(task_dir, killer):
    process = Process(target=wrapper, args=(task_dir, killer))
    process.start()
    process.join()
