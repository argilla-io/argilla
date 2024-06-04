#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from fastapi import APIRouter, Depends

from argilla_server.api.schemas.v1.info import Status, Version
from argilla_server.contexts import info
from argilla_server.search_engine import SearchEngine, get_search_engine

router = APIRouter(tags=["info"])


@router.get("/version", response_model=Version)
async def get_version():
    return Version(version=info.argilla_version())


@router.get("/status", response_model=Status)
async def get_status(search_engine: SearchEngine = Depends(get_search_engine)):
    return Status(
        version=info.argilla_version(),
        search_engine=await search_engine.info(),
        memory=info.memory_status(),
    )
