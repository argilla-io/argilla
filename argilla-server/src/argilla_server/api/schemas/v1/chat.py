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

from typing import List

from argilla_server.pydantic_v1 import BaseModel, StrictStr, validator

MAX_MESSAGE_LENGTH = 5000
MAX_MESSAGE_COUNT = 1000
MAX_ROLE_LENGTH = 20


class ChatMessage(BaseModel):
    role: StrictStr
    content: StrictStr

    @validator("role")
    def validate_role(cls, value):
        # no spaces allowed
        if any([c.isspace() for c in value]):
            raise ValueError("Role must not contain spaces")
        if len(value) > MAX_ROLE_LENGTH:
            raise ValueError(f"Role must be less than {MAX_ROLE_LENGTH} characters")
        return value

    @validator("content")
    def validate_content(cls, value):
        if len(value) > MAX_MESSAGE_LENGTH:
            raise ValueError(f"Content must be less than {MAX_MESSAGE_LENGTH} characters")
        return value
