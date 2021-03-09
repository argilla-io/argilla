"""
This module configures the global fastapi application

"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rubric.server.commons.errors import common_exception_handler

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


app = FastAPI(
    title="Rubric",
    description="Rubric api",
)

configure_middleware(app)
configure_middleware(app)
configure_api_router(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "rubric.server.server:app",
        port=6900,
        host="0.0.0.0",
        reload=True,
        access_log=True,
    )
