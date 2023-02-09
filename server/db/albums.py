from typing import Any, Iterable, Optional, Sequence, Tuple

from pymongo.results import InsertOneResult
from bson import ObjectId

from server.db import client, async_client



async def create_album(name: str, directory: str, parent_album: Optional[str]) -> InsertOneResult:
    document = {
        'name': name,
        'directory': directory,
        'parentAlbum': parent_album,
    }
    result = await client.ai_album.albums.insert_one(document)

    return result


def create_album_sync(name: str, directory: str, parent_album: Optional[str]) -> InsertOneResult:
    document = {
        'name': name,
        'directory': directory,
        'parentAlbum': parent_album,
    }

    return async_client.ai_album.albums.insert_one(document)


async def get_album(id: str):
    result = await client.ai_album.albums.find_one({'_id': ObjectId(id)})

    return result


async def get_albums(query: Any, sort: Any, skip: int, limit: int):
    result = await client.ai_album.albums.find(query).sort(sort).skip(skip).limit(limit).to_list(None)

    return result


async def get_album_media(id: str, sort: Any, skip: int, limit: int):
    result = await client.ai_album.media.find({'albumId': ObjectId(id)}).sort(sort).skip(skip).limit(limit).to_list(None)

    return result
