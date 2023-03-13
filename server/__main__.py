from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
import logging

import asyncio
from threading import Event as TEvent
from multiprocessing import Event as MPEvent
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server import CWD, thread_pool_executor, process_pool_executor
from server.db import async_client, client
from server.routers import albums_router, media_router, faces_router
from server.indexing import image_captioning
from server.indexing import face_detection
from server.indexing import file_indexer
from server.indexing import face_clustering


LOG = logging.getLogger(__name__)
BKG_TASKS = dict()
TASK_KILL_THREADING = TEvent()
TASK_KILL_MPROCESSING = MPEvent()

# async_client.ai_album.drop_collection("albums")
# async_client.ai_album.drop_collection("media")
# async_client.ai_album.drop_collection("faces")
# async_client.ai_album.drop_collection("face_groups")
# async_client.ai_album.media.update_many(
#     {},
#     {"$unset": {"caption": "", "faces": "", "faceEncodings": "", "probs": ""}},
# )

async_client.ai_album.albums.create_index("directory", unique=True)
async_client.ai_album.albums.create_index("parentAlbumIds")
async_client.ai_album.albums.create_index("parentAlbumId")
async_client.ai_album.media.create_index("path", unique=False)
async_client.ai_album.media.create_index("albumIds")


def run_each_task(cwd, thread_killer, process_killer):
    # if not thread_killer.is_set():
    #     file_indexer.run_indexing(CWD)
    # if not thread_killer.is_set():
    #     face_detection.run_face_detection(cwd, process_killer)
    # if not thread_killer.is_set():
    #     face_clustering.run_face_clustering(cwd, thread_killer)
    # if not thread_killer.is_set():
    #     image_captioning.run_image_captioning(cwd, process_killer)
    pass


async def end_tasks():
    LOG.debug("Shutting down background tasks")
    thread_pool_executor.shutdown(wait=False)
    process_pool_executor.shutdown(wait=False)
    TASK_KILL_THREADING.set()
    TASK_KILL_MPROCESSING.set()

    for _, task in BKG_TASKS.items():
        task.cancel()

    with suppress(asyncio.CancelledError):
        for _, task in BKG_TASKS.items():
            await task
    async_client.close()
    client.close()


async def start_tasks():
    LOG.debug("Starting background tasks")
    loop = asyncio.get_running_loop()
    executor = ThreadPoolExecutor(max_workers=8)
    BKG_TASKS["TASKS_WATERFALL"] = loop.run_in_executor(
        executor, run_each_task, CWD, TASK_KILL_THREADING, TASK_KILL_MPROCESSING
    )


def create_app():
    LOG.debug(f"RUNNING FROM - {CWD}")

    LOG.debug("Initiating app")
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(albums_router.router)
    app.include_router(media_router.router)
    app.include_router(faces_router.router)

    @app.on_event("startup")
    async def startup():
        await asyncio.create_task(start_tasks())

    @app.on_event("shutdown")
    async def shutdown():
        await end_tasks()

    LOG.debug("Initiating successful")

    return app


if __name__ == "__main__":
    app = create_app()

    uvicorn.run(app)
