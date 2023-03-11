import logging
import orjson
from fastapi.responses import ORJSONResponse

from bson import ObjectId
from pymongo.cursor import Cursor


LOG = logging.getLogger(__name__)


class WickORJSONResponse(ORJSONResponse):
    media_type = "application/json"


    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, Cursor):
            return list(obj)
        raise TypeError


    def render(self, content: any) -> bytes:
        assert orjson is not None, "orjson must be installed to use ORJSONResponse"
        return orjson.dumps(
            content, 
            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
            default=self.default
        )
