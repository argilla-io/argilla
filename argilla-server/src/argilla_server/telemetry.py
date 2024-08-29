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

import dataclasses
import json
import logging
import platform
from typing import Union

from huggingface_hub.utils import send_telemetry

from argilla_server._version import __version__
from argilla_server.models import (
    Dataset,
    Field,
    FloatMetadataPropertySettings,
    IntegerMetadataPropertySettings,
    MetadataProperty,
    MetadataPropertySettings,
    Question,
    TermsMetadataPropertySettings,
    VectorSettings,
)
from argilla_server.settings import settings
from argilla_server.utils._telemetry import (
    is_running_on_docker_container,
    server_deployment_type,
)

_LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class TelemetryClient:
    enable_telemetry: dataclasses.InitVar[bool] = settings.enable_telemetry

    def __post_init__(self, enable_telemetry: bool):
        self._system_info = {
            "system": platform.system(),
            "machine": platform.machine(),
            "platform": platform.platform(),
            "sys_version": platform.version(),
            "deployment": server_deployment_type(),
            "docker": is_running_on_docker_container(),
        }

        _LOGGER.info("System Info:")
        _LOGGER.info(f"Context: {json.dumps(self._system_info, indent=2)}")
        self.enable_telemetry = enable_telemetry
        self._launch_tracked = False

    async def ensure_server_launch_tracked(self):
        self._launch_tracked = True
        if not self._launch_tracked:
            await self.track_server_launch()

    @staticmethod
    def _process_dataset_settings(dataset: Dataset) -> dict:
        user_data = {}
        attributes: list[str] = [
            "fields",
            "questions",
            "vectors_settings",
            "metadata_properties",
        ]
        for attr in attributes:
            if dataset.is_relationship_loaded(attr):
                user_data[f"num_{attr}"] = len(getattr(dataset, attr))

        return user_data

    @staticmethod
    def _process_dataset_settings_setting(
        setting: Union[
            Field,
            VectorSettings,
            Question,
            FloatMetadataPropertySettings,
            TermsMetadataPropertySettings,
            IntegerMetadataPropertySettings,
        ],
    ) -> dict:
        """
        This method is used to process the dataset settings.

        Args:
            setting: The dataset setting.

        Returns:
            The processed dataset setting.
        """
        user_data = {}
        if isinstance(setting, (Field, Question)):
            user_data["type"] = setting.settings["type"].value
        elif isinstance(
            setting,
            (
                FloatMetadataPropertySettings,
                TermsMetadataPropertySettings,
                IntegerMetadataPropertySettings,
                MetadataProperty,
            ),
        ):
            user_data["type"] = setting.type.value
        elif isinstance(setting, VectorSettings):
            user_data["type"] = "default"
        else:
            raise NotImplementedError("Expected a setting to be processed.")

        return user_data

    async def track_data(self, topic: str, crud_action: str, count: int, user_agent: dict = None) -> None:
        """
        This method is used to track the data.

        Args:
            topic: The topic to track.
            crud_action: The endpoint method.
            user_agent: The user agent.
            count: The count.

        Returns:
            None
        """
        library_name = "argilla"
        topic = f"{library_name}/{topic}"

        user_agent = user_agent or {}
        user_agent.update(self._system_info)
        user_agent["count"] = count or 1
        user_agent["request.endpoint.method"] = crud_action
        await self.ensure_server_launch_tracked()
        send_telemetry(topic=topic, library_name=library_name, library_version=__version__, user_agent=user_agent)

    async def track_crud_dataset(
        self, crud_action: str, dataset: Union[Dataset, None] = None, count: Union[int, None] = None
    ) -> None:
        """
        This method is used to track the creation, update, and deletion of a dataset.

        Args:
            crud_action: The action performed on the dataset.
            dataset: The dataset.
            count: The number of dataset settings.

        Returns:
            None
        """
        topic = "dataset"
        user_agent = self._process_dataset_settings(dataset=dataset)
        await self.track_data(topic=topic, crud_action=crud_action, user_agent=user_agent, count=count)

        attributes: list[str] = ["fields", "questions", "vectors_settings", "metadata_properties"]
        if dataset:
            for attr in attributes:
                if dataset.is_relationship_loaded(attr):
                    obtained_attr_list = getattr(dataset, attr)
                    await self.track_crud_dataset_setting(
                        crud_action=crud_action, setting_name=attr, setting=None, count=len(obtained_attr_list)
                    )
                    for obtained_attr in obtained_attr_list:
                        await self.track_crud_dataset_setting(
                            crud_action=crud_action, setting_name=attr, setting=obtained_attr
                        )

    async def track_crud_dataset_setting(
        self,
        crud_action: str,
        setting_name: str,
        setting: Union[Field, VectorSettings, Question, MetadataPropertySettings, None] = None,
        count: Union[int, None] = None,
    ) -> None:
        """
        This method is used to track the creation, update, and deletion of dataset settings. These
        settings include fields, questions, vectors settings, and metadata properties.

        Args:
            crud_action: The action performed on the dataset setting.
            setting_name: The name of the dataset setting.
            setting: The dataset setting.
            count: The number of dataset settings.

        Returns:
            None
        """
        topic: str = f"dataset/{setting_name}"
        user_agent: dict = self._process_dataset_settings_setting(setting=setting)
        await self.track_data(topic=topic, crud_action=crud_action, user_agent=user_agent, count=count)

    async def track_crud_records(self, crud_action: str, count: Union[int, None] = None) -> None:
        """
        This method is used to track the creation, update, and deletion of records in a dataset.

        Args:
            crud_action: The action performed on the records.
            count: The number of records.

        Returns:
            None
        """
        topic = "dataset/records"
        await self.track_data(topic=topic, crud_action=crud_action, count=count)

    async def track_server_launch(self) -> None:
        """
        This method is used to track the launch of the server.

        Returns:
            None
        """
        topic = "server/launch"
        await self.track_data(topic=topic, crud_action="launch", count=1)


_TELEMETRY_CLIENT = TelemetryClient()


def get_telemetry_client() -> TelemetryClient:
    return _TELEMETRY_CLIENT
