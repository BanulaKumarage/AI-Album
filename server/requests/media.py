import logging

from server.requests import json_response
from server.db import media


LOG = logging.getLogger(__name__)


async def get_media(request):
    LOG.debug(f'get_albums {request}')

    return json_response(
        media.get_media(
                {}, 
                request.query.get('sort', 'name'),
                int(request.query.get('skip', 0)), 
                int(request.query.get('limit', 100)),
            )
        )
