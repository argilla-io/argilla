#  coding=utf-8
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

"""
This module configures the api routes under /api prefix, and
set the required security dependencies if api security is enabled
"""

from fastapi import APIRouter

from argilla.server.apis.v0.handlers import (
    datasets,
    info,
    metrics,
    records,
    records_search,
    records_update,
    text2text,
    text_classification,
    token_classification,
    users,
    workspaces,
)
from argilla.server.errors.base_errors import __ALL__

api_router = APIRouter(responses={error.HTTP_STATUS: error.api_documentation() for error in __ALL__})


dependencies = []

for router in [
    users.router,
    workspaces.router,
    datasets.router,
    info.router,
    metrics.router,
    records.router,
    records_search.router,
    records_update.router,
    text_classification.router,
    token_classification.router,
    text2text.router,
]:
    api_router.include_router(router, dependencies=dependencies)
