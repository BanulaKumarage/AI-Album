import logging
import pathlib

from aiohttp import web
import asyncio
from bson import ObjectId

from server.requests import json_response
from server.db import media
from server import CWD, process_pool_executor
from server.tasks import image_tasks


LOG = logging.getLogger(__name__)


async def get_media(request: web.Request):
    return json_response(
        await media.get_media(
                {}, 
                { '_id': 1 },
                request.query.get('sort', 'name'),
                int(request.query.get('skip', 0)), 
                int(request.query.get('limit', 100)),
            )
        )


async def get_media_by_id(request: web.Request):
    return json_response(await media.get_media_by_id({'_id': ObjectId(request.match_info['id'])}, {}))


async def fetch_thumbnail(request: web.Request):
    item = await media.get_media_by_id({'_id': ObjectId(request.match_info['id'])}, { 'path': 1})
    impath = pathlib.Path(CWD, 'data', item['path'])
    loop = asyncio.get_running_loop()
    stream = await loop.run_in_executor(process_pool_executor, image_tasks.convert_to_thumbnail, impath)

    return web.Response(body=stream.getvalue(), content_type='image/jpeg')


async def fetch_media(request: web.Request):
    item = await media.get_media_by_id({'_id': ObjectId(request.match_info['id'])}, { 'path': 1})
    impath = pathlib.Path(CWD, 'data', item['path'])
    loop = asyncio.get_running_loop()
    stream = await loop.run_in_executor(process_pool_executor, image_tasks.convert_to_image_stream, impath)

    return web.Response(body=stream.getvalue(), content_type='image/jpeg')
