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

from fastapi import FastAPI

from argilla_server._version import __version__ as argilla_version
from argilla_server.apis.v0.handlers import (
    authentication,
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
from argilla_server.apis.v1.handlers import (
    datasets as datasets_v1,
)
from argilla_server.apis.v1.handlers import (
    fields as fields_v1,
)
from argilla_server.apis.v1.handlers import (
    metadata_properties as metadata_properties_v1,
)
from argilla_server.apis.v1.handlers import (
    oauth2 as oauth2_v1,
)
from argilla_server.apis.v1.handlers import (
    questions as questions_v1,
)
from argilla_server.apis.v1.handlers import (
    records as records_v1,
)
from argilla_server.apis.v1.handlers import (
    responses as responses_v1,
)
from argilla_server.apis.v1.handlers import settings as settings_v1
from argilla_server.apis.v1.handlers import (
    suggestions as suggestions_v1,
)
from argilla_server.apis.v1.handlers import (
    users as users_v1,
)
from argilla_server.apis.v1.handlers import (
    vectors_settings as vectors_settings_v1,
)
from argilla_server.apis.v1.handlers import (
    workspaces as workspaces_v1,
)
from argilla_server.errors import APIErrorHandler
from argilla_server.errors.base_errors import __ALL__


def create_api_v0():
    api_v0 = FastAPI(
        title="Argilla v0",
        description="Argilla Server API v0",
        version=str(argilla_version),
        responses={error.HTTP_STATUS: error.api_documentation() for error in __ALL__},
    )
    APIErrorHandler.configure_app(api_v0)

    for router in [
        authentication.router,
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
        api_v0.include_router(router)

    return api_v0


def create_api_v1():
    api_v1 = FastAPI(
        title="Argilla v1",
        description="Argilla Server API v1",
        version=str(argilla_version),
        responses={error.HTTP_STATUS: error.api_documentation() for error in __ALL__},
    )
    # Now, we can control the error responses for the API v1.
    # We keep the same error responses as the API v0 for the moment
    APIErrorHandler.configure_app(api_v1)

    for router in [
        datasets_v1.router,
        fields_v1.router,
        questions_v1.router,
        metadata_properties_v1.router,
        records_v1.router,
        responses_v1.router,
        suggestions_v1.router,
        users_v1.router,
        vectors_settings_v1.router,
        workspaces_v1.router,
        oauth2_v1.router,
        settings_v1.router,
    ]:
        api_v1.include_router(router)

    return api_v1


api_v0 = create_api_v0()
api_v1 = create_api_v1()
