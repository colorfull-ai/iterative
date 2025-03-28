import json
import logging

from datetime import date, datetime, time, timezone
from enum import Enum
from fastapi import Response
from requests import Response as RequestsResponse
from pydantic import BaseModel

from enum import Enum

logger = logging.getLogger(__name__)


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, BaseModel):
            return obj.dict(by_alias=True, exclude_none=True)
        elif isinstance(obj, datetime):
            return (
                obj.replace(tzinfo=timezone.utc).isoformat()
                if obj.tzinfo is None
                else obj.isoformat()
            )
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, time):
            return obj.isoformat()
        elif isinstance(obj, Response):
            # Handle FastAPI Response objects
            return {
                "status_code": obj.status_code,
                "headers": dict(obj.headers),
                "body": str(obj.body) if obj.body else None,
            }
        elif isinstance(obj, RequestsResponse):
            # Handle Requests Response objects
            return {
                "status_code": obj.status_code,
                "headers": dict(obj.headers),
                "body": obj.text,
            }
        elif isinstance(obj, (list, set)):
            return [self.default(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self.default(v) for k, v in obj.items()}
        else:
            return json.JSONEncoder.default(self, obj)