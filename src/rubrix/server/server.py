"""
This module configures the global fastapi application

"""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rubrix.server.commons.errors import common_exception_handler
from rubrix.server.commons.static_rewrite import RewriteStaticFiles

from .commons.settings import settings as api_settings
from .routes import api_router


def configure_middleware(app: FastAPI):
    """Configures fastapi middleware"""

    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def configure_api_exceptions(api: FastAPI):
    """Configures fastapi exception handlers """
    api.exception_handler(500)(common_exception_handler)


def configure_api_router(app: FastAPI):
    """Configures and set the api router to app"""
    app.include_router(api_router, prefix="/api")


def configure_app_statics(app: FastAPI):
    """Configure static folder for app"""
    parent_path = Path(__file__).parent.absolute()

    app.mount(
        "/",
        RewriteStaticFiles(
            directory=os.path.join(parent_path, "static"), html=True, check_dir=False
        ),
        name="static",
    )


app = FastAPI(
    title="Rubrix",
    description="Rubrix API",
    # Disable default openapi configuration
    openapi_url="/api/docs/spec.json",
    docs_url="/api/docs" if api_settings.docs_enabled else None,
    redoc_url=None,
)

for app_configure in [
    configure_middleware,
    configure_api_exceptions,
    configure_api_router,
    configure_app_statics,
]:
    app_configure(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "rubrix.server.server:app",
        port=6900,
        host="0.0.0.0",
        reload=True,
        access_log=True,
    )
