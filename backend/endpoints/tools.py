import os

import redis
from pydantic import BaseModel

class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str

def init_redis() -> redis.Redis:
    host = os.getenv("REDIS_HOST")
    port = int(os.getenv("REDIS_PORT"))
    r = redis.Redis(host=host, port=port)
    return r