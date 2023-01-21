from contextlib import suppress
import os
import pathlib
import logging

from aiohttp import web
import asyncio

from server import load_logger
from server.db import client
import server.db.albums as albums
from server.requests.routes import routes
from server.indexing import indexer, image_processing


LOG = logging.getLogger(__name__)
CWD = pathlib.Path(os.getcwd())

load_logger()

client.ai_album.drop_collection('albums')
client.ai_album.drop_collection('medeia')


async def clean(app):
    client.close()

    app['indexer'].cancel()
    app['image_processing'].cancel()

    with suppress(asyncio.CancelledError):
        await app['indexer']
        await app['image_processing']


async def run_indexer(app):
    LOG.debug('Start indexing')
    app['indexer'] = asyncio.create_task(indexer.run_indexing(CWD))
    app['image_processing'] = asyncio.create_task(image_processing.run_image_processing(CWD))

    yield


def create_app():  
    LOG.debug(f'RUNNING FROM - {CWD}')

    LOG.debug('Initiating app')
    app = web.Application()
    app.add_routes(routes)
    app.on_cleanup.append(clean)
    app.cleanup_ctx.append(run_indexer)
    LOG.debug('Initiating successful')

    return app


if __name__ == '__main__':
    web.run_app(create_app())

