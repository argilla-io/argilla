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
from typing import Optional

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from fastapi import Request
import argilla_server.errors.future as errors


def set_request_error(request: Request, error: Exception) -> None:
    """
    Store the error in the request scope for further processing (Telemetry, etc)

    Parameters:
        error (Exception): The error to store
        request (Request): The request to store the error in

    """

    request.state.error = error


def get_request_error(request: Request) -> Optional[Exception]:
    """
    Get the error stored in the request scope

    Parameters:
        request (Request): The request to get the error from

    Returns:
        Optional[Exception]: The error stored in the request scope, or None if no error is stored
    """

    return getattr(request.state, "error", None)


def add_exception_handlers(app: FastAPI):
    @app.exception_handler(errors.AuthenticationError)
    async def authentication_error(request, exc):
        set_request_error(request, exc)
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            # TODO: Once we move to v2.0 we can remove the content using detail attribute
            # and use the new one using code and message.
            # content={"code": exc.code, "message": exc.message},
            content={"detail": str(exc)},
        )

    @app.exception_handler(errors.NotFoundError)
    async def not_found_error_exception_handler(request, exc):
        set_request_error(request, exc)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            # TODO: Once we move to v2.0 we can remove the content using detail attribute
            # and use the new one using code and message.
            # content={"code": exc.code, "message": exc.message},
            content={"detail": exc.message},
        )

    @app.exception_handler(errors.NotUniqueError)
    async def not_unique_error_exception_handler(request, exc):
        set_request_error(request, exc)
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            # TODO: Once we move to v2.0 we can remove the content using detail attribute
            # and use the new one using code and message.
            # content={"code": exc.code, "message": exc.message},
            content={"detail": exc.message},
        )

    @app.exception_handler(errors.UnprocessableEntityError)
    async def unprocessable_entity_error_exception_handler(request, exc):
        set_request_error(request, exc)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            # TODO: Once we move to v2.0 we can remove the content using detail attribute
            # and use the new one using code and message.
            # content={"code": exc.code, "message": exc.message},
            content={"detail": exc.message},
        )

    # TODO: This is a temporary exception handler for ValueError exceptions.
    # This is because we are using ValueError exceptions in some places and we want to
    # return a 422 status code instead of a 500 status code.
    # This exception handler should be removed once we move to v2.0 and we use UnprocessableEntityError.
    @app.exception_handler(ValueError)
    async def value_error_exception_handler(request, exc):
        set_request_error(request, exc)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": str(exc)},
        )

    # TODO: Once we move to v2.0 we can remove this exception handler and use UnprocessableEntityError
    @app.exception_handler(errors.MissingVectorError)
    async def missing_vector_error_exception_handler(request, exc):
        set_request_error(request, exc)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"code": exc.code, "message": exc.message},
        )

    # TODO: Once we move to v2.0 we can remove this exception handler and use UnprocessableEntityError
    @app.exception_handler(errors.UpdateDistributionWithExistingResponsesError)
    async def update_distribution_with_existing_responses(request, exc):
        set_request_error(request, exc)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"code": exc.code, "message": exc.message},
        )
