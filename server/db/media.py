from typing import Any, Optional
from bson import ObjectId

from server.db import client


def create_media(name: str, path: str, album_id: Optional[str]):
    document = {
        'name': name,
        'path': path,
        'albumId': album_id,
    }
    result = client.ai_album.media.insert_one(document)

    return result


def get_media(query: Any, sort: Any, skip: int, limit: int):
    result = client.ai_album.media.find(query).sort(sort).skip(skip).limit(limit)

    return result


def update_media(filter: Any, update: dict, upsert=False, *args):
    result = client.ai_album.media.update_one(filter, update, upsert, *args)

    return result


def update_medias(filter: Any, update: dict, upsert=False, *args):
    result = client.ai_album.media.update_many(filter, update, upsert, *args)

    return result
