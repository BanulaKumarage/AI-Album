import logging
from fastapi import APIRouter
from bson import ObjectId

import server.db.albums as albums
from server.routers import WickORJSONResponse


LOG = logging.getLogger(__name__)
router = APIRouter()


@router.get("/albums", response_class=WickORJSONResponse)
async def get_albums(
    parent: str = None, sort: str = "name", skip: int = 0, limit: int = 100
):
    LOG.debug(f"get_albums {sort=} {skip=} {limit=}")

    if parent is not None:
        query = {
            "parentAlbumId": None if parent=='null' else ObjectId(parent),
        }
    else:
        query = {}

    return WickORJSONResponse(await albums.get_albums(query, sort, skip, limit))


@router.get("/albums/{id}", response_class=WickORJSONResponse)
async def get_album(id: str):
    LOG.debug(f"get_album {id=}")

    return WickORJSONResponse(await albums.get_album(id))


@router.get("/albums/{id}/media", response_class=WickORJSONResponse)
async def get_album_media(id: str, sort: str = "name", skip: int = 0, limit: int = 100):
    LOG.debug(f"get_album_media {id=}")

    return WickORJSONResponse(await albums.get_album_media(id, sort, skip, limit))
