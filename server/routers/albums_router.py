import logging
from fastapi import APIRouter


import server.db.albums as albums
from server.routers import WickORJSONResponse


LOG = logging.getLogger(__name__)
router = APIRouter()


@router.get('/albums', response_class=WickORJSONResponse)
async def get_albums(sort: str = 'name', skip: int = 0, limit: int = 100):
    LOG.debug(f'get_albums {sort=} {skip=} {limit=}')

    return WickORJSONResponse(await albums.get_albums({}, sort, skip, limit))


@router.get('/albums/{id}', response_class=WickORJSONResponse)
async def get_album(id: str):
    LOG.debug(f'get_album {id=}')

    return WickORJSONResponse(await albums.get_album(id))


@router.get('/albums/{id}/media', response_class=WickORJSONResponse)
async def get_album_media(id: str, sort: str = 'name', skip: int = 0, limit: int = 100):
    LOG.debug(f'get_album_media {id=}')

    return WickORJSONResponse(await albums.get_album_media(id, sort, skip, limit))
