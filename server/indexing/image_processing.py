import hashlib
import os
import pathlib
import traceback
import logging
import glob
from typing import Optional

import asyncio
import networkx as nx

from server.db import albums, media


LOG = logging.getLogger(__name__)


async def run_image_processing(dir):
    pass