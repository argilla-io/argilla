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
import os
from pathlib import Path

from brotli_asgi import BrotliMiddleware
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ConfigError

from rubrix import __version__ as rubrix_version
from rubrix.logging import configure_logging
from rubrix.server.apis.v0.settings.server import settings
from rubrix.server.apis.v0.settings.server import settings as api_settings
from rubrix.server.daos.datasets import DatasetsDAO
from rubrix.server.daos.records import DatasetRecordsDAO
from rubrix.server.elasticseach.client_wrapper import create_es_wrapper
from rubrix.server.errors import APIErrorHandler
from rubrix.server.routes import api_router
from rubrix.server.security import auth
from rubrix.server.static_rewrite import RewriteStaticFiles


def configure_middleware(app: FastAPI):
    """Configures fastapi middleware"""

    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(BrotliMiddleware, minimum_size=512, quality=7)


def configure_api_exceptions(api: FastAPI):
    """Configures fastapi exception handlers"""
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
        import opensearchpy

        try:
            es_wrapper = create_es_wrapper()
            dataset_records: DatasetRecordsDAO = DatasetRecordsDAO(es_wrapper)
            datasets: DatasetsDAO = DatasetsDAO.get_instance(
                es_wrapper, records_dao=dataset_records
            )
            datasets.init()
            dataset_records.init()
        except opensearchpy.exceptions.ConnectionError as error:
            raise ConfigError(
                f"Your Elasticsearch endpoint at {settings.obfuscated_elasticsearch()} "
                "is not available or not responding.\n"
                "Please make sure your Elasticsearch instance is launched and correctly running and\n"
                "you have the necessary access permissions. "
                "Once you have verified this, restart the Rubrix server.\n"
            ) from error


def configure_app_security(app: FastAPI):

    if hasattr(auth, "router"):
        app.include_router(auth.router)


def configure_app_logging(app: FastAPI):
    """Configure app logging using"""
    app.on_event("startup")(configure_logging)


app = FastAPI(
    title="Rubrix",
    description="Rubrix API",
    # Disable default openapi configuration
    openapi_url="/api/docs/spec.json",
    docs_url="/api/docs" if api_settings.docs_enabled else None,
    redoc_url=None,
    version=str(rubrix_version),
)

for app_configure in [
    configure_app_logging,
    configure_middleware,
    configure_api_exceptions,
    configure_app_security,
    configure_api_router,
    configure_app_statics,
    configure_app_storage,
]:
    app_configure(app)
