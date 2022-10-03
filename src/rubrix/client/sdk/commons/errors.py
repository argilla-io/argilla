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


class RubrixClientError(Exception):
    pass


class ApiCompatibilityError(RubrixClientError):
    def __init__(self, min_version: str):
        self.min_version = min_version

    def __str__(self):
        return (
            "\nThe rubrix server does not support this functionality."
            f"\nPlease, use the client with a {self.min_version} version server instance."
        )


class RubrixApiResponseError(RubrixClientError):

    HTTP_STATUS: int

    def __init__(self, **ctx):
        self.ctx = ctx

    def __str__(self):
        return (
            f"Rubrix server returned an error with http status: {self.HTTP_STATUS}"
            + f"\nError details: [{self.ctx}]"
        )


class NotFoundApiError(RubrixApiResponseError):
    HTTP_STATUS = 404


class ValidationApiError(RubrixApiResponseError):
    HTTP_STATUS = 422

    def __init__(self, client_ctx, params, **ctx):

        for error in params.get("errors", []):
            current_level = client_ctx
            for loc in error["loc"]:
                new_value = None
                try:
                    new_value = current_level[loc]
                except KeyError:
                    pass
                if new_value is None:
                    break
                if hasattr(new_value, "dict"):
                    new_value = new_value.dict()
                current_level = new_value
            error["value"] = current_level

        # TODO: parse error details and match with client context
        super().__init__(**ctx, params=params)


class BadRequestApiError(RubrixApiResponseError):
    HTTP_STATUS = 400


class UnauthorizedApiError(RubrixApiResponseError):
    HTTP_STATUS = 401


class ForbiddenApiError(RubrixApiResponseError):
    HTTP_STATUS = 403


class AlreadyExistsApiError(RubrixApiResponseError):
    HTTP_STATUS = 409


class MethodNotAllowedApiError(RubrixApiResponseError):
    HTTP_STATUS = 405


class GenericApiError(RubrixApiResponseError):
    HTTP_STATUS = 500
