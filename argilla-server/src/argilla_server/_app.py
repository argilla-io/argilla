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
import contextlib
import glob
import inspect
import logging
import os
import shutil
import tempfile
from pathlib import Path

import backoff
from brotli_asgi import BrotliMiddleware
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from argilla_server import helpers
from argilla_server._version import __version__ as argilla_version
from argilla_server.apis.routes import api_v0, api_v1
from argilla_server.constants import DEFAULT_API_KEY, DEFAULT_PASSWORD, DEFAULT_USERNAME
from argilla_server.contexts import accounts
from argilla_server.daos.backend import GenericElasticEngineBackend
from argilla_server.daos.backend.base import GenericSearchError
from argilla_server.daos.datasets import DatasetsDAO
from argilla_server.daos.records import DatasetRecordsDAO
from argilla_server.database import get_async_db
from argilla_server.logging import configure_logging
from argilla_server.models import User
from argilla_server.pydantic_v1.errors import ConfigError
from argilla_server.security import auth
from argilla_server.settings import settings
from argilla_server.static_rewrite import RewriteStaticFiles

_LOGGER = logging.getLogger("argilla")


def create_server_app() -> FastAPI:
    """Configure the argilla server"""

    app = FastAPI(
        title="Argilla",
        description="Argilla API",
        docs_url=None,
        redoc_url=None,
        version=str(argilla_version),
    )

    @app.get("/docs", include_in_schema=False)
    async def redirect_docs():
        return RedirectResponse(url=f"{settings.base_url}api/docs")

    @app.get("/api", include_in_schema=False)
    async def redirect_api():
        return RedirectResponse(url=f"{settings.base_url}api/docs")

    for app_configure in [
        configure_app_logging,
        configure_database,
        configure_storage,
        configure_telemetry,
        configure_middleware,
        configure_app_security,
        configure_api_router,
        configure_app_statics,
    ]:
        app_configure(app)

    # This if-else clause is needed to simplify the test dependencies setup. Otherwise we cannot override dependencies
    # easily. We can review this once we have separate fastapi application for the api and the webapp.
    if settings.base_url and settings.base_url != "/":
        _app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
        _app.mount(settings.base_url, app)
        return _app
    else:
        return app


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


def configure_api_router(app: FastAPI):
    """Configures and set the api router to app"""
    app.mount("/api/v1", api_v1)
    app.mount("/api", api_v0)


def configure_app_statics(app: FastAPI):
    """Configure static folder for app"""

    parent_path = Path(__file__).parent.absolute()
    statics_folder = Path(os.path.join(parent_path, "static"))
    if not (statics_folder.exists() and statics_folder.is_dir()):
        return

    def _create_statics_folder(path_from):
        """
        Application statics will be created with a parameterized baseUrl variable.

        This function will replace the variable by the real runtime value found in settings.base_url

        This allow us to deploy the argilla server under a custom base url, even when webapp does not
        support it.

        """
        BASE_URL_VAR_NAME = "@@baseUrl@@"
        temp_dir = tempfile.mkdtemp()
        new_folder = shutil.copytree(path_from, temp_dir + "/statics")
        base_url = helpers.remove_suffix(settings.base_url, suffix="/")
        for extension in ["*.js", "*.html"]:
            for file in glob.glob(
                f"{new_folder}/**/{extension}",
                recursive=True,
            ):
                helpers.replace_string_in_file(
                    file,
                    string=BASE_URL_VAR_NAME,
                    replace_by=base_url,
                )

        return new_folder

    temp_statics = _create_statics_folder(statics_folder)

    app.mount(
        "/",
        RewriteStaticFiles(directory=temp_statics, html=True, check_dir=False),
        name="static",
    )


def configure_storage(app: FastAPI):
    def _on_backoff(event):
        _LOGGER.warning(
            f"Connection to {settings.obfuscated_elasticsearch()} is not ready. "
            f"Tried {event['tries']} times. Retrying..."
        )

    @backoff.on_exception(
        lambda: backoff.constant(interval=15),
        ConfigError,
        max_time=60,
        on_backoff=_on_backoff,
    )
    def _setup_elasticsearch():
        try:
            backend = GenericElasticEngineBackend.get_instance()
            dataset_records: DatasetRecordsDAO = DatasetRecordsDAO(backend)
            datasets: DatasetsDAO = DatasetsDAO.get_instance(
                es=backend,
                records_dao=dataset_records,
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

    @app.on_event("startup")
    async def setup_elasticsearch():
        _setup_elasticsearch()


def configure_app_security(app: FastAPI):
    auth.configure_app(app)


def configure_app_logging(app: FastAPI):
    """Configure app logging using"""
    app.on_event("startup")(configure_logging)


def configure_telemetry(app: FastAPI):
    message = "\n"
    message += inspect.cleandoc(
        """
        Argilla uses telemetry to report anonymous usage and error information.

        You can know more about what information is reported at:

            https://docs.argilla.io/en/latest/reference/telemetry.html

        Telemetry is currently enabled. If you want to disable it, you can configure
        the environment variable before relaunching the server:
    """
    )
    message += "\n\n    "
    message += "#set ARGILLA_ENABLE_TELEMETRY=0" if os.name == "nt" else "$>export ARGILLA_ENABLE_TELEMETRY=0"
    message += "\n"

    @app.on_event("startup")
    async def check_telemetry():
        if settings.enable_telemetry:
            print(message, flush=True)


_get_db_wrapper = contextlib.asynccontextmanager(get_async_db)


def configure_database(app: FastAPI):
    def _user_has_default_credentials(user: User):
        return user.api_key == DEFAULT_API_KEY or accounts.verify_password(DEFAULT_PASSWORD, user.password_hash)

    def _log_default_user_warning():
        _LOGGER.warning(
            f"User {DEFAULT_USERNAME!r} with default credentials has been found in the database. "
            "If you are using argilla in a production environment this can be a serious security problem. "
            f"We recommend that you create a new admin user and then delete the default {DEFAULT_USERNAME!r} one."
        )

    @app.on_event("startup")
    async def log_default_user_warning_if_present():
        async with _get_db_wrapper() as db:
            default_user = await accounts.get_user_by_username(db, DEFAULT_USERNAME)
            if default_user and _user_has_default_credentials(default_user):
                _log_default_user_warning()


app = create_server_app()
