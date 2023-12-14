from typing import List, Literal, Optional, Union, overload
from uuid import UUID

from argilla.sdk import _api as api
from argilla.sdk._collections import ConfigurationCollection
from argilla.sdk._models import DatasetConfiguration
from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
from argilla.client.workspaces import Workspace


class Dataset(RemoteFeedbackDataset):
    id: UUID
    status: Literal["draft", "ready"]

    @property
    def config(self) -> ConfigurationCollection:
        return ConfigurationCollection(self)

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
