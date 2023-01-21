import os
import pathlib
import logging

from aiohttp import web

from server import load_logger
from server.db import client
import server.db.albums as albums
from server.requests.routes import routes
from server.indexing import indexer


LOG = logging.getLogger(__name__)
CWD = pathlib.Path(os.getcwd())

load_logger()

client.ai_album.drop_collection('albums')
client.ai_album.drop_collection('medeia')

async def clean(app):
    client.close()


def create_app():  
    LOG.debug(f'RUNNING FROM - {CWD}')
    
    LOG.debug('Start indexing')
    indexer.run_indexing(CWD)
    LOG.debug('Finished indexing')

    LOG.debug('Initiating app')
    app = web.Application()
    app.add_routes(routes)
    app.on_cleanup.append(clean)
    LOG.debug('Initiating successful')

    return app


if __name__ == '__main__':
    web.run_app(create_app())

