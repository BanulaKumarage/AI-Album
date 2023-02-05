import pathlib

from aiohttp import web

from server.requests import albums
from server.requests import media
from server.requests import utils
from server import CWD


routes = [
    # album queries
    web.get('/albums', albums.get_albums),
    web.get('/albums/{id}', albums.get_album),
    web.get('/albums/{id}/media', albums.get_album_media),

    # Media queries
    web.get('/media', media.get_media),
    web.get('/media/{id}', media.get_media_by_id),

    # indexing
    # web.get('/media', media.get_media),

    # static
    web.static('/static', str(pathlib.Path(CWD).joinpath('data')), follow_symlinks=True),
    web.get('/thumbnail/{id}', media.fetch_thumbnail),
    web.get('/fullsize/{id}', media.fetch_media)
]
