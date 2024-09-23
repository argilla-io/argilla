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

from argilla_server.pydantic_v1 import BaseModel, Field

MIN_MESSAGE_LENGTH = 1
MAX_MESSAGE_LENGTH = 20000

MIN_ROLE_LENGTH = 1
MAX_ROLE_LENGTH = 20
MAX_ROLE_REGEX = r"^\S+$"


class ChatFieldValue(BaseModel):
    role: str = Field(..., min_role_length=MIN_ROLE_LENGTH, max_length=MAX_ROLE_LENGTH, regex=MAX_ROLE_REGEX)
    content: str = Field(..., min_message_length=MIN_MESSAGE_LENGTH, max_length=MAX_MESSAGE_LENGTH)
