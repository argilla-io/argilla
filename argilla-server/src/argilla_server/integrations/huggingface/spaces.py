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

# from argilla_server.pydantic_v1 import BaseSettings, Field
from pydantic import Field
from pydantic_settings import BaseSettings


class HuggingfaceSettings(BaseSettings):
    space_id: Optional[str] = Field(None, alias="SPACE_ID")
    space_title: Optional[str] = Field(None, alias="SPACE_TITLE")
    space_subdomain: Optional[str] = Field(None, alias="SPACE_SUBDOMAIN")
    space_host: Optional[str] = Field(None, alias="SPACE_HOST")
    space_repo_name: Optional[str] = Field(None, alias="SPACE_REPO_NAME")
    space_author_name: Optional[str] = Field(None, alias="SPACE_AUTHOR_NAME")
    # NOTE: Hugging Face has a typo in their environment variable name,
    # using PERSISTANT instead of PERSISTENT. We will use the correct spelling in our code.
    space_persistent_storage_enabled: bool = Field(False, alias="PERSISTANT_STORAGE_ENABLED")

    @property
    def is_running_on_huggingface(self) -> bool:
        return bool(self.space_id)


HUGGINGFACE_SETTINGS = HuggingfaceSettings()
