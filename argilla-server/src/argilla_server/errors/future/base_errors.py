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

__all__ = ["NotFoundError", "NotUniqueError", "UnprocessableEntityError", "AuthenticationError"]

UNPROCESSABLE_ENTITY_ERROR_CODE = "unprocessable_entity"
MISSING_VECTOR_ERROR_CODE = "missing_vector"


class NotFoundError(Exception):
    """Custom Argilla not found error. Use it for situations where an Argilla domain entity has not be found on the system."""

    pass


class NotUniqueError(Exception):
    """Custom Argilla not unique error. Use it for situations where an Argilla domain entity already exists violating a constraint."""

    pass


class UnprocessableEntityError(Exception):
    """Custom Argilla unprocessable entity error. Use it for situations where an Argilla domain entity can not be processed."""

    def __init__(self, message, code=UNPROCESSABLE_ENTITY_ERROR_CODE):
        self.message = message
        self.code = code


class AuthenticationError(Exception):
    """Custom Argilla unauthorized error. Use it for situations where an request is not authorized to perform an action."""

    pass
