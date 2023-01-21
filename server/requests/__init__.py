import json
from typing import Iterable

from bson import ObjectId, json_util
from aiohttp import web
from pymongo.cursor import Cursor



def json_response(data):
    if isinstance(data, Cursor):
        list_cur = list(data)
        json_data = json_util.dumps(list_cur) 
        
        return web.json_response(text=json_data)

    return web.json_response(text=json_util.dumps(data))
