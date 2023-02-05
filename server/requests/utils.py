from io import BytesIO
import pathlib

import asyncio
from aiohttp import web
from aiohttp.web import Request

from server import CWD, process_pool_executor
from server.tasks import image_tasks


