from fastapi import FastAPI

from rubrix.server.api.v1 import api_v1

apis = FastAPI()
apis.mount("/v1", api_v1)
