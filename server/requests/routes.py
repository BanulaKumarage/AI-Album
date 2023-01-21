from aiohttp import web

from server.requests import albums
from server.requests import media
from server.indexing import indexer


routes = [
    # album queries
    web.get('/albums', albums.get_albums),
    web.get('/albums/{id}', albums.get_album),

    # Media queries
    web.get('/media', media.get_media),

    # indexing
    # web.get('/media', media.get_media),
]
