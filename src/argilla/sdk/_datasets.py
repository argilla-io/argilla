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

from typing import List, Literal, Optional, Union, overload
from uuid import UUID

from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
from argilla.client.workspaces import Workspace
from argilla.sdk import _api as api
from argilla.sdk import _models as models
from argilla.sdk._collections import FieldsCollection, QuestionsCollection
from argilla.sdk._models import DatasetConfiguration


class _Configuration:
    def __init__(self, dataset: "Dataset"):
        self.dataset = dataset
        self.fields = FieldsCollection(dataset)
        self.questions = QuestionsCollection(dataset)

    @property
    def guidelines(self) -> str:
        return self.dataset.guidelines

    @property
    def allow_extra_metadata(self) -> bool:
        return self.dataset.allow_extra_metadata

    def to_dict(self) -> dict:
        return {
            "guidelines": self.guidelines,
            "allow_extra_metadata": self.allow_extra_metadata,
            "fields": [f.to_dict() for f in self.fields.list()],
            "questions": [q.to_dict() for q in self.questions.list()],
        }

    def create(self, config: models.DatasetConfiguration) -> "_Configuration":
        self.update(config.guidelines, config.allow_extra_metadata)

        for field in config.fields:
            self.fields.create(field)

        for question in config.questions:
            self.questions.create(question)

        return self

    def update(self, guidelines: Optional[str] = None, allow_extra_metadata: Optional[bool] = None) -> "_Configuration":
        kwargs = {}

        if guidelines is not None:
            kwargs["guidelines"] = guidelines
        if allow_extra_metadata is not None:
            kwargs["allow_extra_metadata"] = allow_extra_metadata
        if len(kwargs) == 0:
            raise ValueError("At least one of the parameters must be specified")

        api.Dataset.update(self.dataset.id, **kwargs)

        if guidelines is not None:
            self.dataset._guidelines = guidelines
        if allow_extra_metadata is not None:
            self.dataset._allow_extra_metadata = allow_extra_metadata

        return self


class Dataset(RemoteFeedbackDataset):
    id: UUID
    status: Literal["draft", "ready"]

    @property
    def config(self) -> _Configuration:
        return _Configuration(self)

    @classmethod
    def list(cls) -> List["Dataset"]:
        datasets = api.Dataset.list()
        return [cls._construct_dataset_from_api_model(dataset) for dataset in datasets]

    @classmethod
    def by_id(cls, dataset_id: Union[str, UUID]) -> "Dataset":
        dataset = api.Dataset.get(dataset_id)
        return cls._construct_dataset_from_api_model(dataset)

    @classmethod
    def by_name_and_workspace(cls, name: str, workspace: Workspace) -> Optional["Dataset"]:
        datasets = cls.list()
        for dataset in datasets:
            if dataset.name == name and workspace.id == dataset.workspace.id:
                return dataset

    @classmethod
    @overload
    def create(cls, name: str, workspace: Workspace) -> "Dataset":
        ...

    @classmethod
    @overload
    def create(cls, name: str, workspace: Workspace, config: DatasetConfiguration, publish: bool = False) -> "Dataset":
        ...

    @classmethod
    def create(
        cls, name: str, workspace: Workspace, config: Optional[DatasetConfiguration] = None, publish: bool = False
    ) -> "Dataset":
        dataset_ = api.Dataset.create(
            name=name,
            workspace_id=workspace.id,
            guidelines=config.guidelines if config else None,
            allow_extra_metadata=config.allow_extra_metadata if config else None,
        )

        dataset = cls._construct_dataset_from_api_model(dataset_)

        if config:
            try:
                dataset.config.create(config)

                if publish:
                    dataset.publish()

            except Exception:
                api.Dataset.delete(dataset.id)
                raise

        return dataset

    @classmethod
    def delete_by_id(cls, dataset_id: Union[str, UUID]) -> None:
        api.Dataset.delete(dataset_id)

    @classmethod
    def publish_by_id(cls, dataset_id: Union[str, UUID]) -> "Dataset":
        dataset = api.Dataset.publish(dataset_id)
        return cls._construct_dataset_from_api_model(dataset)

    def delete(self) -> None:
        self.delete_by_id(self.id)

    def publish(self) -> "Dataset":
        return self.publish_by_id(self.id)

    @classmethod
    def _construct_dataset_from_api_model(cls, dataset: api.Dataset):
        from argilla.sdk import default_http_client

        return cls(
            id=dataset.id,
            name=dataset.name,
            workspace=Workspace.from_id(dataset.workspace_id),
            guidelines=dataset.guidelines,
            created_at=dataset.inserted_at,
            updated_at=dataset.updated_at,
            # This code is for backward compatibility and should be removed in the future
            client=default_http_client,
            # End of backward compatibility code
        )
