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

from typing import AsyncGenerator

from ..settings import settings
from .base import *  # noqa
from .base import SearchEngine
from .elasticsearch import ElasticSearchEngine
from .opensearch import OpenSearchEngine


async def get_search_engine() -> AsyncGenerator[SearchEngine, None]:
    async with SearchEngine.get_by_name(settings.search_engine) as engine:
        yield engine
