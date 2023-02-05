import logging

from aiohttp.web import Request

from server.requests import json_response
import server.db.albums as albums


LOG = logging.getLogger(__name__)


async def get_albums(request: Request):
    LOG.debug(f'get_albums {request}')

    return json_response(
        await albums.get_albums(
                {}, 
                request.query.get('sort', 'name'),
                int(request.query.get('skip', 0)), 
                int(request.query.get('limit', 10)),
            )
        )


async def get_album(request: Request):
    LOG.debug(f'get_album {request.match_info}')

    return json_response(await albums.get_album(request.match_info.get('id', None)))



async def get_album_media(request):
    LOG.debug(f'get_album_media {request.match_info}')

    return json_response(
        await albums.get_album_media(
                request.match_info.get('id'), 
                request.query.get('sort', 'name'),
                int(request.query.get('skip', 0)), 
                int(request.query.get('limit', 10)),
            )
        )
