from io import BytesIO
import pathlib

import asyncio
from aiohttp import web
from aiohttp.web import Request

from server import CWD, process_pool_executor
from server.tasks import image_tasks


async def fetch_thumbnail(req: Request):
    impath = pathlib.Path(CWD, 'data', req.path[11:])
    loop = asyncio.get_running_loop()
    stream = await loop.run_in_executor(process_pool_executor, image_tasks.convert_to_thumbnail, impath)

    return web.Response(body=stream.getvalue(), content_type='image/jpeg')


async def fetch_media(req: Request):
    im_id = req.path[10:]
    loop = asyncio.get_running_loop()
    stream = await loop.run_in_executor(process_pool_executor, image_tasks.convert_to_image_stream, im_id)

    return web.Response(body=stream.getvalue(), content_type='image/jpeg')
