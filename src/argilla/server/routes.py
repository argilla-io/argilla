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
from typing import List

from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError

from argilla.server.apis.v0.handlers import (
    datasets,
    info,
    metrics,
    records,
    records_search,
    records_update,
    security,
    text2text,
    text_classification,
    token_classification,
    users,
    workspaces,
)
from argilla.server.apis.v1.handlers import (
    datasets as datasets_v1,
    fields as fields_v1,
    questions as questions_v1,
    records as records_v1,
    responses as responses_v1,
    suggestions as suggestions_v1,
    users as users_v1,
    workspaces as workspaces_v1,
)
from argilla.server.errors import (
    APIErrorHandler,
    BadRequestError,
    ClosedDatasetError,
    EntityAlreadyExistsError,
    EntityNotFoundError,
    ForbiddenOperationError,
    InvalidTextSearchError,
    MissingInputParamError,
    UnauthorizedError,
    ValidationError,
    WrongTaskError,
)


def configure_api_v0(parent: FastAPI):
    return _configure_api_app(
        parent,
        router_list=[
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
            security.router,
        ],
    )


def configure_api_v1(parent: FastAPI):
    return _configure_api_app(
        parent,
        router_list=[
            datasets_v1.router,
            fields_v1.router,
            questions_v1.router,
            records_v1.router,
            responses_v1.router,
            users_v1.router,
            workspaces_v1.router,
            suggestions_v1.router,
        ],
    )


def _configure_api_exceptions(api: FastAPI):
    """Configures fastapi exception handlers"""
    api.exception_handler(Exception)(APIErrorHandler.common_exception_handler)
    api.exception_handler(EntityNotFoundError)(APIErrorHandler.common_exception_handler)
    api.exception_handler(UnauthorizedError)(APIErrorHandler.common_exception_handler)
    api.exception_handler(ForbiddenOperationError)(APIErrorHandler.common_exception_handler)
    api.exception_handler(EntityAlreadyExistsError)(APIErrorHandler.common_exception_handler)
    api.exception_handler(ClosedDatasetError)(APIErrorHandler.common_exception_handler)
    api.exception_handler(ValidationError)(APIErrorHandler.common_exception_handler)
    api.exception_handler(AssertionError)(APIErrorHandler.common_exception_handler)
    api.exception_handler(WrongTaskError)(APIErrorHandler.common_exception_handler)
    api.exception_handler(MissingInputParamError)(APIErrorHandler.common_exception_handler)
    api.exception_handler(RequestValidationError)(APIErrorHandler.common_exception_handler)
    api.exception_handler(InvalidTextSearchError)(APIErrorHandler.common_exception_handler)
    api.exception_handler(BadRequestError)(APIErrorHandler.common_exception_handler)


def _configure_api_app(parent: FastAPI, router_list: List[APIRouter]):
    api = FastAPI(dependency_overrides_provider=parent)

    for router in router_list:
        api.include_router(router)

    _configure_api_exceptions(api)

    return api
