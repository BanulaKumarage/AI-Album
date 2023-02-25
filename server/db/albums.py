from typing import Any, Iterable, Optional, Sequence, Tuple

from pymongo.results import InsertOneResult
from bson import ObjectId

from server.db import client, async_client


async def create_album(
    name: str, directory: str, parent_album: Optional[str]
) -> InsertOneResult:
    document = {
        "name": name,
        "directory": directory,
        "parentAlbum": parent_album,
    }
    result = await client.ai_album.albums.insert_one(document)

    return result


async def get_album(id: str):
    result = await client.ai_album.albums.find_one({"_id": ObjectId(id)})

    return result


async def get_album_sync(query: dict):
    result = await client.ai_album.albums.find_one(query)

    return result


async def get_albums(query: Any, sort: Any, skip: int, limit: int):
    print(query)
    if len(query) > 0:
        get_albums_pipeline = [
            {
                "$match": query,
            },
            {
                "$lookup": {
                    "from": "albums",
                    "localField": "_id",
                    "foreignField": "parentAlbumId",
                    "as": "result",
                },
            },
            {
                "$addFields": {
                    "hasChildren": {
                        "$gt": [
                            {
                                "$size": "$result",
                            },
                            0,
                        ],
                    },
                },
            },
            {
                "$project": {
                    "name": 1,
                    "hasChildren": 1,
                },
            },
            {
                "$sort": {
                    f"{sort}": 1
                }
            },
            {
                "$limit": limit
            }
        ]
        result = await client.ai_album.albums.aggregate(get_albums_pipeline).to_list(None)
        return result

    result = (
        await client.ai_album.albums.find(query)
        .sort(sort)
        .skip(skip)
        .limit(limit)
        .to_list(None)
    )

    return result


async def get_album_media(id: str, sort: Any, skip: int, limit: int):
    all_albums_pipeline = [
        {
            # get the album
            "$match": {
                "_id": ObjectId(id),
            },
        },
        {
            # get all child albums
            "$lookup": {
                "from": "albums",
                "localField": "_id",
                "foreignField": "parentAlbumIds",
                "as": "result",
            },
        },
        {
            # combine album ids into one array
            "$project": {
                "allAlbums": {
                    "$reduce": {
                        "initialValue": [],
                        "input": [["$_id"], "$result._id"],
                        "in": {
                            "$concatArrays": ["$$value", "$$this"],
                        },
                    },
                },
            },
        },
        {
            # get all media that has all these album ids
            "$lookup": {
                "from": "media",
                "localField": "allAlbums",
                "foreignField": "albumIds",
                "as": "result1",
            },
        },
        {
            # custom projection
            "$project": {
                "_id": 0,
                "result1": 1,
            },
        },
        {
            # make a big array
            "$unwind": {
                "path": "$result1",
            },
        },
        # make it the root, sort, skip and return the result
        {"$replaceRoot": {"newRoot": "$result1"}},
        {"$sort": {f"{sort}": 1}},
        {"$skip": skip},
        {"$limit": limit},
    ]
    result = await client.ai_album.albums.aggregate(all_albums_pipeline).to_list(None)

    return result
