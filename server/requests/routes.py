from io import BytesIO
import pathlib

from aiohttp import web
from aiohttp.web import Request
from PIL import Image

from server.requests import albums
from server.requests import media
from server.indexing import indexer
from server import CWD
from server.conf import thumbnail_resolution


async def fetch_thumbnail(req: Request):
    impath = pathlib.Path(CWD, 'data', req.path[11:])
    print(impath)
    im = Image.open(impath)
    stream = BytesIO()
    im.thumbnail(thumbnail_resolution)
    im.save(stream, 'jpeg')
    return web.Response(body=stream.getvalue(), content_type='image/jpeg')


routes = [
    # album queries
    web.get('/albums', albums.get_albums),
    web.get('/albums/{id}', albums.get_album),

    # Media queries
    web.get('/media', media.get_media),

    # indexing
    # web.get('/media', media.get_media),

    # static
    web.static('/static', str(pathlib.Path(CWD).joinpath('data')), follow_symlinks=True),
    web.get('/thumbnail/{none:.*}', fetch_thumbnail)
]
