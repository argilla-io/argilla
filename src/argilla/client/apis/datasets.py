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

import warnings
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union

from pydantic import BaseModel, Field

from argilla.client.apis import AbstractApi, api_compatibility
from argilla.client.sdk.commons.errors import (
    AlreadyExistsApiError,
    ForbiddenApiError,
    NotFoundApiError,
)
from argilla.client.sdk.datasets.api import get_dataset
from argilla.client.sdk.datasets.models import TaskType


@dataclass
class _AbstractSettings:
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "_AbstractSettings":
        """
        Creates a settings instance from a plain python dictionary

        Args:
            data: The data dict

        Returns:
            A new ``cls`` settings instance
        """
        raise NotImplementedError()


@dataclass
class LabelsSchemaSettings(_AbstractSettings):
    """
    A base dataset settings class for labels schema management

    Args:
        label_schema: The label's schema for the dataset

    """

    label_schema: Set[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LabelsSchemaSettings":
        label_schema = data.get("label_schema", {})
        labels = {label["name"] for label in label_schema.get("labels", [])}
        return cls(label_schema=labels)


@dataclass
class TextClassificationSettings(LabelsSchemaSettings):
    """
    The settings for text classification datasets

    Args:
        label_schema: The label's schema for the dataset

    """


@dataclass
class TokenClassificationSettings(LabelsSchemaSettings):
    """
    The settings for token classification datasets

    Args:
        label_schema: The label's schema for the dataset

    """


Settings = Union[TextClassificationSettings, TokenClassificationSettings]

__TASK_TO_SETTINGS__ = {
    TaskType.text_classification: TextClassificationSettings,
    TaskType.token_classification: TokenClassificationSettings,
}


class Datasets(AbstractApi):
    """Dataset client api class"""

    _API_PREFIX = "/api/datasets"

    __SETTINGS_MIN_API_VERSION__ = "0.15"

    DEFAULT_SCAN_SIZE = 250

    class _DatasetApiModel(BaseModel):
        name: str
        task: TaskType
        owner: Optional[str] = None
        created_at: Optional[datetime] = None
        last_updated: Optional[datetime] = None

        tags: Dict[str, str] = Field(default_factory=dict)
        metadata: Dict[str, Any] = Field(default_factory=dict)

    class _SettingsApiModel(BaseModel):
        label_schema: Dict[str, Any]

    def find_by_name(self, name: str) -> _DatasetApiModel:
        dataset = get_dataset(self.http_client, name=name).parsed
        return self._DatasetApiModel.parse_obj(dataset)

    def create(self, name: str, settings: Settings):
        task = (
            TaskType.text_classification
            if isinstance(settings, TextClassificationSettings)
            else TaskType.token_classification
        )

        with api_compatibility(self, min_version=self.__SETTINGS_MIN_API_VERSION__):
            dataset = self._DatasetApiModel(name=name, task=task)
            self.http_client.post(f"{self._API_PREFIX}", json=dataset.dict())
            self.__save_settings__(dataset, settings=settings)

    def configure(self, name: str, settings: Settings):
        """
        Configures dataset settings. If dataset does not exist, a new one will be created.
        Pass only settings that want to configure

        Args:
            name: The dataset name
            settings: The dataset settings
        """
        try:
            self.create(name=name, settings=settings)
        except AlreadyExistsApiError:
            ds = self.find_by_name(name)
            self.__save_settings__(dataset=ds, settings=settings)

    def scan(
        self,
        name: str,
        projection: Optional[Set[str]] = None,
        limit: Optional[int] = None,
        id_from: Optional[str] = None,
        **query,
    ) -> Iterable[dict]:
        """
        Search records over a dataset

        Args:
            name: the dataset
            query: the search query
            projection: a subset of record fields to retrieve. If not provided,
            limit: The number of records to retrieve
            id_from: If provided, starts gathering the records starting from that Record.
                As the Records returned with the load method are sorted by ID, ´id_from´
                can be used to load using batches.
            only id's will be returned

        Returns:

            An iterable of raw object containing per-record info

        """

        url = (
            f"{self._API_PREFIX}/{name}/records/:search?limit={self.DEFAULT_SCAN_SIZE}"
        )
        query = self._parse_query(query=query)

        if limit == 0:
            limit = None

        request = {
            "fields": list(projection) if projection else ["id"],
            "query": query,
        }

        if id_from:
            request["next_idx"] = id_from

        yield_fields = 0
        with api_compatibility(self, min_version="1.2.0"):
            response = self.http_client.post(
                url,
                json=request,
            )

            while response.get("records"):
                for record in response["records"]:
                    yield record
                    yield_fields += 1
                    if limit and limit <= yield_fields:
                        return

                next_idx = response.get("next_idx")
                if next_idx:
                    response = self.http_client.post(
                        path=url,
                        json={**request, "next_idx": next_idx},
                    )

    def update_record(
        self,
        name: str,
        record_id: str,
        **content,
    ):
        with api_compatibility(self, min_version="1.2.0"):
            url = f"{self._API_PREFIX}/{name}/records/{record_id}"
            response = self.http_client.patch(
                path=url,
                json=content,
            )
            return response

    def delete_records(
        self,
        name: str,
        mark_as_discarded: bool = False,
        discard_when_forbidden: bool = True,
        **query: Optional[dict],
    ) -> Tuple[int, int]:
        """
        Tries to delete records in a dataset for a given query/ids list.

        Args:
            name: The dataset name
            query: The query matching records
            ids: A list of records ids. If provided, the query param will be ignored
            mark_as_discarded: If `True`, the matched records will be marked as `Discarded` instead
                of delete them
            discard_when_forbidden: Only super-user or dataset creator can delete records from a dataset.
                So, running "hard" deletion for other users will raise an `ForbiddenApiError` error.
                If this parameter is `True`, the client API will automatically try to mark as ``Discarded``
                records instead.

        Returns:
            The total of matched records and real number of processed errors. These numbers could not
            be the same if some data conflicts are found during operations (some matched records change during
            deletion).

        """
        with api_compatibility(self, min_version="0.18"):
            try:
                query = self._parse_query(query=query)
                response = self.http_client.delete(
                    path=f"{self._API_PREFIX}/{name}/data?mark_as_discarded={mark_as_discarded}",
                    json=query,
                )
                return response["matched"], response["processed"]
            except ForbiddenApiError as faer:
                if discard_when_forbidden:
                    warnings.warn(
                        message=f"{faer}. Records will be discarded instead",
                        category=UserWarning,
                    )
                    return self.delete_records(
                        name=name,
                        query=query,
                        mark_as_discarded=True,
                        discard_when_forbidden=False,  # Next time will raise the error
                    )
                else:
                    raise faer

    def __save_settings__(self, dataset: _DatasetApiModel, settings: Settings):
        if __TASK_TO_SETTINGS__.get(dataset.task) != type(settings):
            raise ValueError(
                f"The provided settings type {type(settings)} cannot be applied to dataset."
                " Task type mismatch"
            )

        settings_ = self._SettingsApiModel(
            label_schema={"labels": [label for label in settings.label_schema]}
        )

        with api_compatibility(self, min_version=self.__SETTINGS_MIN_API_VERSION__):
            self.http_client.put(
                f"{self._API_PREFIX}/{dataset.task}/{dataset.name}/settings",
                json=settings_.dict(),
            )

    def load_settings(self, name: str) -> Optional[Settings]:
        """
        Load the dataset settings

        Args:
            name: The dataset name

        Returns:
            Settings defined for the dataset
        """
        dataset = self.find_by_name(name)
        try:
            with api_compatibility(self, min_version=self.__SETTINGS_MIN_API_VERSION__):
                response = self.http_client.get(
                    f"{self._API_PREFIX}/{dataset.task}/{dataset.name}/settings"
                )
                return __TASK_TO_SETTINGS__.get(dataset.task).from_dict(response)
        except NotFoundApiError:
            return None
