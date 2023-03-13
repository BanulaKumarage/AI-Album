import pathlib
import logging
import gc
from threading import Thread
from multiprocessing import Process, Event

from PIL import Image
import numpy as np

from server.db import async_client
from server.conf import (
    face_detection_workers_per_device,
    face_detection_batch_size,
    supported_image_types,
    face_detector,
    face_model,
)
from server.indexing.utils import DataLoader
from server.utils.image_processing import rotate_image

import insightface
from insightface.app import FaceAnalysis


LOG = logging.getLogger(__name__)
BATCH_SIZE = face_detection_batch_size
DETECTOR = face_detector
FACE_MODEL = face_model


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

    def record_faces(self, entry, faces, probs, encodings):
        async_client.ai_album.media.update_one(
            {"_id": entry["_id"]},
            {
                "$set": {
                    "faces": faces,
                    "probs": probs,
                    "faceEncodings": encodings,
                }
            },
        )

    def run(self) -> None:
        fetch = True
        LOG.debug(f"Starting face detection worker {self.worker_id}")

        app = FaceAnalysis(providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
        app.prepare(ctx_id=0, det_size=(640, 640), det_thresh=0.8)

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
                open_cv_image = np.array(image)
                open_cv_image = open_cv_image[:, :, ::-1].copy()

                try:
                    faces = app.get(image)
                    faces_count += len(faces)
                    faces_new = []

                    for face in faces:
                        face["bbox"] = face["bbox"].tolist()
                        faces_new.append(
                            {
                                "left": face["bbox"][0],
                                "top": face["bbox"][1],
                                "right": face["bbox"][2],
                                "bottom": face["bbox"][3],
                            }
                        )

                    self.record_faces(
                        entry,
                        faces_new,
                        [face["det_score"].tolist() for face in faces],
                        [face["embedding"].tolist() for face in faces],
                    )
                except:
                    continue

            LOG.debug(
                f"{self.worker_id} Detected {faces_count} faces in {BATCH_SIZE} images"
            )
            self.processed += faces_count

        LOG.debug(
            f"FACE_DETECTION_WORKER {self.worker_id} proceessed {self.processed} images. "
            + ("Exit by kill!" if self.killer.is_set() else "")
        )


def wrapper(task_dir, killer):
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

    for device in ["CPU"]:
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
