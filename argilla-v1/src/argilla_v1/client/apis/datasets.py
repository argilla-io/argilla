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

import math
import warnings
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union

from argilla_v1.client.apis import AbstractApi, api_compatibility
from argilla_v1.client.sdk.commons.errors import (
    AlreadyExistsApiError,
    ApiCompatibilityError,
    ForbiddenApiError,
    NotFoundApiError,
)
from argilla_v1.client.sdk.datasets.api import get_dataset
from argilla_v1.client.sdk.datasets.models import TaskType
from argilla_v1.pydantic_v1 import BaseModel, Field


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

    label_schema: List[str]

    def __post_init__(self):
        if not isinstance(self.label_schema, (set, list, tuple)):
            raise ValueError(
                f"`label_schema` is of type={type(self.label_schema)}, but type=set is preferred, and also both type=list and type=tuple are allowed."
            )
        self.label_schema = self._get_unique_labels()

    def _get_unique_labels(self) -> List[str]:
        unique_labels = []
        for label in self.label_schema:
            if label not in unique_labels:
                unique_labels.append(label)
        return unique_labels

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LabelsSchemaSettings":
        label_schema = data.get("label_schema", {})
        labels = [label["name"] for label in label_schema.get("labels", [])]
        return cls(label_schema=labels)

    @property
    def label2id(self) -> Dict[str, int]:
        return {label: i for i, label in enumerate(self.label_schema)}

    @property
    def id2label(self) -> Dict[int, str]:
        return {i: label for i, label in enumerate(self.label_schema)}


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

    class _DatasetApiModel(BaseModel):
        id: Optional[str]
        name: str
        task: TaskType
        owner: Optional[str] = None
        workspace: Optional[str] = None
        created_at: Optional[datetime] = None
        last_updated: Optional[datetime] = None

        tags: Dict[str, str] = Field(default_factory=dict)
        metadata: Dict[str, Any] = Field(default_factory=dict)

    class _SettingsApiModel(BaseModel):
        label_schema: Dict[str, Any]

    def find_by_name(self, name: str, workspace: Optional[str] = None) -> _DatasetApiModel:
        dataset = get_dataset(self.http_client, name=name, workspace=workspace).parsed
        return self._DatasetApiModel.parse_obj(dataset)

    def create(self, name: str, task: TaskType, workspace: str) -> _DatasetApiModel:
        try:
            with api_compatibility(self, min_version="1.4.0"):
                dataset = self._DatasetApiModel(name=name, task=task, workspace=workspace)
                self.http_client.post(f"{self._API_PREFIX}", json=dataset.dict())
        except ApiCompatibilityError:
            dataset = self._DatasetApiModel(name=name, task=task)
            self.http_client.post(f"{self._API_PREFIX}?workspace={workspace}", json=dataset.dict())
        return dataset

    def configure(self, name: str, workspace: str, settings: Settings):
        """
        Configures dataset settings. If dataset does not exist, a new one will be created.
        Pass only settings that want to configure

        Args:
            name: The dataset name
            workspace: The dataset workspace
            settings: The dataset settings
        """
        try:
            task = (
                TaskType.text_classification
                if isinstance(settings, TextClassificationSettings)
                else TaskType.token_classification
            )
            ds = self.create(name=name, task=task, workspace=workspace)
        except AlreadyExistsApiError:
            ds = self.find_by_name(name, workspace=workspace)
        self._save_settings(dataset=ds, settings=settings)

    def scan(
        self,
        name: str,
        projection: Optional[Set[str]] = None,
        limit: Optional[int] = None,
        sort: Optional[List[Tuple[str, str]]] = None,
        id_from: Optional[str] = None,
        batch_size: int = 250,
        **query,
    ) -> Iterable[dict]:
        """
        Search records over a dataset

        Args:
            name: the dataset
            query: the search query
            projection: a subset of record fields to retrieve. If not provided,
                 only id's will be returned
            sort: The fields on which to sort [(<field_name>, 'asc|decs')].
            limit: The number of records to retrieve
            id_from: If provided, starts gathering the records starting from that Record.
                As the Records returned with the load method are sorted by ID, ´id_from´
                can be used to load using batches.
            batch_size: If provided, load `batch_size` samples per request. A lower batch
                size may help avoid timeouts.

        Returns:
            An iterable of raw object containing per-record info
        """

        if limit and limit < 0:
            raise ValueError("The scan limit must be non-negative.")

        limit = limit if limit else math.inf
        url = f"{self._API_PREFIX}/{name}/records/:search?limit={{limit}}"
        query = self._parse_query(query=query)

        request = {
            "fields": list(projection) if projection else ["id"],
            "query": query,
        }

        if sort is not None:
            try:
                if isinstance(sort, list):
                    assert all([(isinstance(item, tuple)) and (item[-1] in ["asc", "desc"]) for item in sort])
                else:
                    raise Exception()
            except Exception:
                raise ValueError("sort must be a dict formatted as List[Tuple[<field_name>, 'asc|desc']]")
            request["sort_by"] = [{"id": item[0], "order": item[-1]} for item in sort]

        elif id_from:
            # TODO: Show message since sort + next_id is not compatible since fixes a sort by id
            request["next_idx"] = id_from

        with api_compatibility(self, min_version="1.2.0"):
            request_limit = min(limit, batch_size)
            response = self.http_client.post(
                url.format(limit=request_limit),
                json=request,
            )

            while response.get("records"):
                yield from response["records"]
                limit -= request_limit
                if limit <= 0:
                    return

                next_request_params = {k: response[k] for k in ["next_idx", "next_page_cfg"] if response.get(k)}
                if not next_request_params:
                    return

                request_limit = min(limit, batch_size)
                response = self.http_client.post(
                    path=url.format(limit=request_limit),
                    json={**request, **next_request_params},
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

    def _save_settings(self, dataset: _DatasetApiModel, settings: Settings):
        if __TASK_TO_SETTINGS__.get(dataset.task) != type(settings):
            raise ValueError(
                f"The provided settings type {type(settings)} cannot be applied to dataset. Task type mismatch"
            )

        settings_ = self._SettingsApiModel.parse_obj(
            {"label_schema": {"labels": [label for label in settings.label_schema]}}
        )

        try:
            with api_compatibility(self, min_version="1.4"):
                self.http_client.patch(
                    f"{self._API_PREFIX}/{dataset.name}/{dataset.task.value}/settings?workspace={dataset.workspace}",
                    json=settings_.dict(),
                )
        except ApiCompatibilityError:
            with api_compatibility(self, min_version="0.15"):
                self.http_client.put(
                    f"{self._API_PREFIX}/{dataset.task.value}/{dataset.name}/settings",
                    json=settings_.dict(),
                )

    def load_settings(self, name: str, workspace: Optional[str] = None) -> Optional[Settings]:
        """
        Load the dataset settings

        Args:
            name: The dataset name
            workspace: The workspace name where the dataset belongs to

        Returns:
            Settings defined for the dataset
        """
        dataset = self.find_by_name(name, workspace=workspace)
        try:
            with api_compatibility(self, min_version="1.0"):
                params = {"workspace": dataset.workspace} if dataset.workspace else {}
                response = self.http_client.get(
                    f"{self._API_PREFIX}/{dataset.name}/{dataset.task.value}/settings", params=params
                )
                return __TASK_TO_SETTINGS__.get(dataset.task).from_dict(response)
        except NotFoundApiError:
            return None
        except Exception:
            return None
