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
This module configures the global fastapi application
"""
import inspect
import os
import sys
import warnings
from pathlib import Path

from brotli_asgi import BrotliMiddleware
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ConfigError

from argilla import __version__ as argilla_version
from argilla.logging import configure_logging
from argilla.server.daos.backend.elasticsearch import (
    ElasticsearchBackend,
    GenericSearchError,
)
from argilla.server.daos.datasets import DatasetsDAO
from argilla.server.daos.records import DatasetRecordsDAO
from argilla.server.errors import APIErrorHandler, EntityNotFoundError
from argilla.server.routes import api_router
from argilla.server.security import auth
from argilla.server.settings import settings
from argilla.server.static_rewrite import RewriteStaticFiles


def configure_middleware(app: FastAPI):
    """Configures fastapi middleware"""

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(BrotliMiddleware, minimum_size=512, quality=7)


def configure_api_exceptions(api: FastAPI):
    """Configures fastapi exception handlers"""
    api.exception_handler(EntityNotFoundError)(APIErrorHandler.common_exception_handler)
    api.exception_handler(Exception)(APIErrorHandler.common_exception_handler)
    api.exception_handler(RequestValidationError)(
        APIErrorHandler.common_exception_handler
    )


def configure_api_router(app: FastAPI):
    """Configures and set the api router to app"""
    app.include_router(api_router, prefix="/api")


def configure_app_statics(app: FastAPI):
    """Configure static folder for app"""
    parent_path = Path(__file__).parent.absolute()
    statics_folder = Path(os.path.join(parent_path, "static"))
    if not (statics_folder.exists() and statics_folder.is_dir()):
        return

    app.mount(
        "/",
        RewriteStaticFiles(
            directory=statics_folder,
            html=True,
            check_dir=False,
        ),
        name="static",
    )


def configure_app_storage(app: FastAPI):
    @app.on_event("startup")
    async def configure_elasticsearch():
        try:
            es_wrapper = ElasticsearchBackend.get_instance()
            dataset_records: DatasetRecordsDAO = DatasetRecordsDAO(es_wrapper)
            datasets: DatasetsDAO = DatasetsDAO.get_instance(
                es_wrapper, records_dao=dataset_records
            )
            datasets.init()
            dataset_records.init()
        except GenericSearchError as error:
            raise ConfigError(
                f"Your Elasticsearch endpoint at {settings.obfuscated_elasticsearch()} "
                "is not available or not responding.\n"
                "Please make sure your Elasticsearch instance is launched and correctly running and\n"
                "you have the necessary access permissions. "
                "Once you have verified this, restart the argilla server.\n"
            ) from error


def configure_app_security(app: FastAPI):

    if hasattr(auth, "router"):
        app.include_router(auth.router)


def configure_app_logging(app: FastAPI):
    """Configure app logging using"""
    app.on_event("startup")(configure_logging)


app = FastAPI(
    title="argilla",
    description="argilla API",
    # Disable default openapi configuration
    openapi_url="/api/docs/spec.json",
    docs_url="/api/docs" if settings.docs_enabled else None,
    redoc_url=None,
    version=str(argilla_version),
)


def configure_telemetry(app):
    message = "\n"
    message += inspect.cleandoc(
        """
        Rubrix uses telemetry to report anonymous usage and error information.

        You can know more about what information is reported at:

            https://rubrix.readthedocs.io/en/stable/reference/telemetry.html

        Telemetry is currently enabled. If you want to disable it, you can configure
        the environment variable before relaunching the server:
    """
    )
    message += "\n\n    "
    message += (
        "#set RUBRIX_ENABLE_TELEMETRY=0"
        if os.name == "nt"
        else "$>export RUBRIX_ENABLE_TELEMETRY=0"
    )
    message += "\n"

    @app.on_event("startup")
    async def check_telemetry():
        if settings.enable_telemetry:
            print(message, flush=True)


for app_configure in [
    configure_app_logging,
    configure_middleware,
    configure_api_exceptions,
    configure_app_security,
    configure_api_router,
    configure_app_statics,
    configure_app_storage,
    configure_telemetry,
]:
    app_configure(app)
