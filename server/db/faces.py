from typing import Any, Optional
from bson import ObjectId
import base64

from server.db import client


async def get_media_by_face_group(group: str, sort: Any, skip: int, limit: int):
    media_by_face_group_pipeline = [
        {
            "$match": {
                "groupId": ObjectId(group),
            },
        },
        {"$project": {"imageId": 1}},
        {"$group": {"_id": "$imageId"}},
        {
            "$lookup": {
                "from": "media",
                "localField": "_id",
                "foreignField": "_id",
                "as": "result",
            },
        },
        {
            "$unwind": {
                "path": "$result",
            },
        },
        {
            "$replaceRoot": {
                "newRoot": {"$mergeObjects": [{"groupId": ObjectId(group)}, "$result"]},
            },
        },
        {
            "$project": {"_id": 1, "groupId": 1},
        },
        {"$sort": {f"{sort}": 1}},
        {"$skip": skip},
        {"$limit": limit},
    ]

    result = await client.ai_album.faces.aggregate(
        media_by_face_group_pipeline
    ).to_list(None)

    return result


async def get_faces(query: Any, projection: Any, sort: Any, skip: int, limit: int):
    result = (
        await client.ai_album.faces.find(query, projection=projection)
        .sort(sort)
        .skip(skip)
        .limit(limit)
        .to_list(None)
    )
    return result


async def get_face_groups(
    query: Any, projection: Any, sort: Any, skip: int, limit: int
):
    print(sort, skip, limit)
    result = (
        await client.ai_album.face_groups.find(query, projection=projection)
        .sort(sort)
        .skip(skip)
        .limit(limit)
        .to_list(None)
    )
    return result
