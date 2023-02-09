from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
import logging

import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server import CWD, thread_pool_executor, process_pool_executor
from server.db import client
from server.routers import albums_router, media_router
from server.indexing import file_indexer, image_processing


LOG = logging.getLogger(__name__)
BKG_TASKS = dict()

# client.ai_album.drop_collection('albums')
# client.ai_album.drop_collection('media')


async def end_tasks():
    LOG.debug('Shutting down')
    client.close()
    thread_pool_executor.shutdown(wait=False)
    process_pool_executor.shutdown(wait=False)

    # TODO there is no way to cancel tasks running in executors, find a workaround
    # https://stackoverflow.com/questions/26413613/asyncio-is-it-possible-to-cancel-a-future-been-run-by-an-executor
    # BKG_TASKS['file_indexer'].cancel()
    # BKG_TASKS['image_processing'].cancel()

    # with suppress(asyncio.CancelledError):
    #     await BKG_TASKS['file_indexer']
        # await BKG_TASKS['image_processing']
    return


async def start_tasks():
    LOG.debug('Starting up')
    loop = asyncio.get_running_loop()
    executor = ThreadPoolExecutor(max_workers=8)
    # BKG_TASKS['file_indexer'] = loop.run_in_executor(executor, file_indexer.run_indexing, CWD)
    # BKG_TASKS['image_processing'] = loop.run_in_executor(executor, image_processing.run_image_processing, CWD)


def create_app():  
    LOG.debug(f'RUNNING FROM - {CWD}')

    LOG.debug('Initiating app')
    app = FastAPI()
    app.add_middleware(CORSMiddleware, 
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
    app.include_router(albums_router.router)
    app.include_router(media_router.router)

    @app.on_event('startup')
    async def startup():
        await asyncio.create_task(start_tasks())

    @app.on_event('shutdown')
    async def shutdown():
        await end_tasks()

    LOG.debug('Initiating successful')

    return app


if __name__ == '__main__':
    app = create_app()

    uvicorn.run(app)

