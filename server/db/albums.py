from typing import Any, Iterable, Optional, Sequence, Tuple

from pymongo.results import InsertOneResult
from bson import ObjectId

from server.db import client




def create_album(name: str, directory: str, parent_album: Optional[str]) -> InsertOneResult:
    document = {
        'name': name,
        'directory': directory,
        'parentAlbum': parent_album,
    }
    result = client.ai_album.albums.insert_one(document)

    return result


def get_album(id: str):
    result = client.ai_album.albums.find_one({'_id': ObjectId(id)})

    return result


def get_albums(query: Any, sort: Any, skip: int, limit: int):
    result = client.ai_album.albums.find(query).sort(sort).skip(skip).limit(limit)

    return result


def get_album_media(id: str, sort: Any, skip: int, limit: int):
    result = client.ai_album.media.find({'albumId': ObjectId(id)}).sort(sort).skip(skip).limit(limit)

    return result
