from typing import List
from fastapi import APIRouter

from logging import getLogger

logger = getLogger(__name__)

router = APIRouter()

@router.get("/hello")
async def hello():
    return {"message": "hello"}
