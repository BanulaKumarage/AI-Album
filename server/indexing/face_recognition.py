import pathlib
import logging
from threading import Event, Thread

from PIL import Image
import torch
import numpy as np
import face_recognition, face_recognition_models
import dlib

from server.db import async_client
from server.conf import face_dtection_workers_per_gpu
from server.indexing.utils import DataLoader


LOG = logging.getLogger(__name__)
MAX_WIDTH = 2048
MAX_HEIGHT = 2048


# TODO need to have images scaled to same size
class BatchFaceDetector:
    def __init__(self, device: int) -> None:
        dlib.cuda.set_device(device)
        self.cnn_face_detection_model = (
            face_recognition_models.cnn_face_detector_model_location()
        )
        self.cnn_face_detector = dlib.cnn_face_detection_model_v1(
            self.cnn_face_detection_model
        )

    def detect_batch(
        self, images, number_of_times_to_upsample=1, batch_size=128
    ) -> list:
        def convert_cnn_detections_to_css(detections):
            return [
                face_recognition.api._trim_css_to_bounds(
                    face_recognition.api._rect_to_css(face.rect), images[0].shape
                )
                for face in detections
            ]

        raw_detections_batched = self.cnn_face_detector(
            images, number_of_times_to_upsample, batch_size
        )

        return list(map(convert_cnn_detections_to_css, raw_detections_batched))


class FaceDetector:
    def __init__(self, cuda=False, device: int = 0) -> None:
        self.cuda = cuda
        if self.cuda:
            dlib.cuda.set_device(device)
        self.cnn_face_detection_model = (
            face_recognition_models.cnn_face_detector_model_location()
        )
        self.cnn_face_detector = dlib.cnn_face_detection_model_v1(
            self.cnn_face_detection_model
        )

    def detect(self, image, number_of_times_to_upsample=1):
        model = "cnn" if self.cuda else "hog"

        if model == "cnn":
            return [
                face_recognition.api._trim_css_to_bounds(
                    face_recognition.api._rect_to_css(face.rect), image.shape
                )
                for face in face_recognition.api._raw_face_locations(
                    image, number_of_times_to_upsample, "cnn"
                )
            ]
        else:
            return [
                face_recognition.api._trim_css_to_bounds(
                    face_recognition.api._rect_to_css(face), image.shape
                )
                for face in face_recognition.api._raw_face_locations(
                    image, number_of_times_to_upsample, model
                )
            ]


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
        self.detector = FaceDetector(self.cuda, self.device_name)

    def run(self) -> None:
        fetch = True
        LOG.debug(f"Starting face dtection worker {self.worker_id}")

        while fetch and not self.killer.is_set():
            data = self.data_loader.get_next_batch()
            fetch = len(data) > 0

            for entry in data:
                if self.killer.is_set():
                    break
                path = (
                    pathlib.Path()
                    .joinpath(self.task_dir, "data", entry["path"])
                    .as_posix()
                )

                image = Image.open(path).convert("RGB")
                ratio = min(MAX_WIDTH / image.width, MAX_HEIGHT / image.height)

                if ratio < 1:
                    image = image.resize(
                        (round(image.width * ratio), round(image.height * ratio))
                    )

                image = np.array(image)
                LOG.debug(f"Running image {image.shape}")
                faces = self.detector.detect(image)
                if ratio < 1:
                    faces = [
                        (
                            int(top * (1 / ratio)),
                            int(right * (1 / ratio)),
                            int(bottom * (1 / ratio)),
                            int(left * (1 / ratio)),
                        )
                        for (top, right, bottom, left) in faces
                    ]
                self.processed += 1

                LOG.debug(faces)
                async_client.ai_album.media.update_one(
                    {"_id": entry["_id"]},
                    {"$set": {"faces": faces}},
                )
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
                {"path": {"$regex": "jpg$|JPG$|JPEG$|jpeg$"}},
            ]
        },
        {"_id": 1, "path": 1},
        "name",
        100,
    )

    if data_loader.get_count() == 0:
        LOG.debug(f"Face detection not needed")
        return

    LOG.debug(f"Face detection needed for {data_loader.get_count()}.")

    if device_count > 0:
        workers = []
        for d in range(device_count):
            for w in range(face_dtection_workers_per_gpu):
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
