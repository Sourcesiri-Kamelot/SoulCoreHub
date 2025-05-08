from dataclasses import dataclass
from typing import Literal, NamedTuple

class _FluminaRoute(NamedTuple):
    method: Literal["websocket", "get", "put", "post", "delete"]
    path: str

def gen_wrapper(method, path):
    def wrapper(fn):
        fn._flumina_route = _FluminaRoute(method, path)
        return fn

    return wrapper

def websocket(path: str):
    return gen_wrapper("websocket", path)

def get(path: str):
    return gen_wrapper("get", path)

def put(path: str):
    return gen_wrapper("put", path)

def post(path: str):
    return gen_wrapper("post", path)

def delete(path: str):
    return gen_wrapper("delete", path)

