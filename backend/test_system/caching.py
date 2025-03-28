import os
import pickle
from abc import ABC, abstractmethod
from collections.abc import Buffer
from typing import Any

import redis


def init_redis() -> redis.Redis:
    host = os.getenv("REDIS_HOST")
    port = int(os.getenv("REDIS_PORT"))
    r = redis.Redis(host=host, port=port)
    return r


class CachingInterface(ABC):
    def __init__(self, key: str, data: Any):
        self.key = key
        self.data = data

    @abstractmethod
    def write(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    @staticmethod
    @abstractmethod
    def load(key: str) -> Any:
        pass


class RedisCachingException(Exception):
    pass


class RedisCaching(CachingInterface):
    def __init__(self, key: str, data: Any, expire: int | None = None):
        super().__init__(key, data)
        self.expire = expire

    def write(self):
        r = init_redis()
        if r.get(self.key) is not None:
            raise RedisCachingException("Key already exists")
        if self.expire is not None:
            r.setex(self.key, self.expire, pickle.dumps(self.data))
        else:
            r.set(self.key, pickle.dumps(self.data))

    def update(self):
        r = init_redis()
        if r.get(self.key) is None:
            raise RedisCachingException("Key does not exist")
        r.set(self.key, pickle.dumps(self.data))

    def delete(self):
        r = init_redis()
        if r.get(self.key) is None:
            raise RedisCachingException("Key does not exist")
        r.delete(self.key)

    @staticmethod
    def load(key: str) -> Any:
        r = init_redis()
        res: Buffer = r.get(key)
        if res is None:
            raise RedisCachingException("Key does not exist")
        return pickle.loads(res)