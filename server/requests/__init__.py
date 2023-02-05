import json
from typing import Iterable

from bson import ObjectId, json_util
from aiohttp import web
from pymongo.cursor import Cursor


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, Cursor):
            return JSONEncoder().encode(list(o))
        return json.JSONEncoder.default(self, o)


def json_response(data):
    return web.json_response(text=JSONEncoder().encode(data))
