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

from typing import Union

from argilla_server.api.schemas.v1.settings import ArgillaSettings, Settings, HuggingfaceSettings
from argilla_server.integrations.huggingface.spaces import HUGGINGFACE_SETTINGS
from argilla_server.settings import settings


def get_settings() -> Settings:
    return Settings(
        argilla=_get_argilla_settings(),
        huggingface=_get_huggingface_settings(),
    )


def _get_argilla_settings() -> ArgillaSettings:
    argilla_settings = ArgillaSettings()

    if _get_huggingface_settings():
        argilla_settings.show_huggingface_space_persistent_storage_warning = (
            settings.show_huggingface_space_persistent_storage_warning
        )

    return argilla_settings


def _get_huggingface_settings() -> Union[HuggingfaceSettings, None]:
    if HUGGINGFACE_SETTINGS.is_running_on_huggingface:
        return HuggingfaceSettings.model_validate(HUGGINGFACE_SETTINGS)
