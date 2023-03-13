import logging
import pathlib

from fastapi import APIRouter
from fastapi.responses import Response
from bson import ObjectId
import asyncio

from server.routers import WickORJSONResponse
from server.db import media
from server import CWD, process_pool_executor
from server.utils import image_processing
from server.conf import supported_image_types


LOG = logging.getLogger(__name__)
router = APIRouter()


@router.get("/media", response_class=WickORJSONResponse)
async def get_media(sort: str = "name", skip: int = 0, limit: int = 100):
    return WickORJSONResponse(await media.get_media({}, {"_id": 1}, sort, skip, limit))


@router.get("/media/{id}")
async def get_media_by_id(id: str):
    return WickORJSONResponse(await media.get_media_by_id({"_id": ObjectId(id)}, {}))


@router.get("/thumbnail/{id}", response_class=Response)
async def fetch_thumbnail(
    id: str, top: int | float = -1, right: int | float = -1, bottom: int | float = -1, left: int | float = -1
):
    item = await media.get_media_by_id({"_id": ObjectId(id)}, {"path": 1})
    impath = pathlib.Path(CWD, "data", item["path"])

    if impath.suffix.lstrip(".") not in supported_image_types:
        impath = pathlib.Path(__file__).parent.joinpath(
            "assets", "media-place-holder.png"
        )
        top = -1
        right = -1
        bottom = -1
        left = -1
    
    loop = asyncio.get_running_loop()
    stream = await loop.run_in_executor(
        process_pool_executor,
        image_processing.convert_to_thumbnail,
        impath,
        int(top),
        int(right),
        int(bottom),
        int(left),
    )

    return Response(stream.getvalue(), media_type="image/jpeg")


@router.get("/fullsize/{id}", response_class=Response)
async def fetch_media(id: str):
    item = await media.get_media_by_id({"_id": ObjectId(id)}, {"path": 1})
    impath = pathlib.Path(CWD, "data", item["path"])

    if impath.suffix.lstrip(".") not in supported_image_types:
        impath = pathlib.Path(__file__).parent.joinpath(
            "assets", "media-place-holder.png"
        )

    loop = asyncio.get_running_loop()
    stream = await loop.run_in_executor(
        process_pool_executor, image_processing.convert_to_image_stream, impath
    )

    return Response(stream.getvalue(), media_type="image/jpeg")
