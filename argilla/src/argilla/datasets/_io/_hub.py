# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import warnings
from collections import defaultdict
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any, Dict, Optional, Type, Union, Literal
from uuid import UUID

from datasets import DatasetDict
from datasets.data_files import EmptyDatasetError
from PIL import Image

from argilla._exceptions import ImportDatasetError
from argilla._exceptions._api import UnprocessableEntityError
from argilla._exceptions._records import RecordsIngestionError
from argilla._exceptions._settings import SettingsError
from argilla._helpers._media import pil_to_data_uri
from argilla.datasets._io._disk import DiskImportExportMixin
from argilla.records._io._datasets import HFDatasetsIO
from argilla.records._mapping import IngestedRecordMapper
from argilla.responses import Response

if TYPE_CHECKING:
    from datasets import Dataset as HFDataset

    from argilla import Argilla, Dataset, Settings, Workspace


class HubImportExportMixin(DiskImportExportMixin):
    def to_hub(
        self: "Dataset",
        repo_id: str,
        *,
        with_records: bool = True,
        generate_card: Optional[bool] = True,
        **kwargs: Any,
    ) -> None:
        """Pushes the `Dataset` to the Hugging Face Hub. If the dataset has been previously pushed to the
        Hugging Face Hub, it will be updated instead of creating a new dataset repo.

        Parameters:
            repo_id: the ID of the Hugging Face Hub repo to push the `Dataset` to.
            with_records: whether to load the records from the Hugging Face dataset. Defaults to `True`.
            generate_card: whether to generate a dataset card for the `Dataset` in the Hugging Face Hub. Defaults
                to `True`.
            **kwargs: the kwargs to pass to `datasets.Dataset.push_to_hub`.

        Returns:
            None
        """

        from huggingface_hub import DatasetCardData, HfApi

        from argilla.datasets._io.card import (
            ArgillaDatasetCard,
            size_categories_parser,
        )

        hf_api = HfApi(token=kwargs.get("token"))

        hfds = False
        if with_records:
            hfds = self.records(with_vectors=True, with_responses=True, with_suggestions=True).to_datasets()
            hfds.push_to_hub(repo_id, **kwargs)
        else:
            hf_api.create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=kwargs.get("exist_ok") or True)

        with TemporaryDirectory() as tmpdirname:
            config_dir = os.path.join(tmpdirname)

            self.to_disk(path=config_dir, with_records=False)

            if generate_card:
                sample_argilla_record = next(iter(self.records(with_suggestions=True, with_responses=True)))
                sample_huggingface_record = self._get_sample_hf_record(hfds) if with_records else None
                dataset_size = len(hfds) if with_records else 0
                card = ArgillaDatasetCard.from_template(
                    card_data=DatasetCardData(
                        size_categories=size_categories_parser(dataset_size),
                        tags=["rlfh", "argilla", "human-feedback"],
                    ),
                    repo_id=repo_id,
                    argilla_fields=self.settings.fields,
                    argilla_questions=self.settings.questions,
                    argilla_guidelines=self.settings.guidelines or None,
                    argilla_vectors_settings=self.settings.vectors or None,
                    argilla_metadata_properties=self.settings.metadata,
                    argilla_record=sample_argilla_record.to_dict(),
                    huggingface_record=sample_huggingface_record,
                )
                card.save(filepath=os.path.join(tmpdirname, "README.md"))

            hf_api.upload_folder(
                folder_path=tmpdirname,
                repo_id=repo_id,
                repo_type="dataset",
            )

    @classmethod
    def from_hub(
        cls: Type["Dataset"],
        repo_id: str,
        *,
        name: Optional[str] = None,
        workspace: Optional[Union["Workspace", str]] = None,
        client: Optional["Argilla"] = None,
        with_records: bool = True,
        settings: Union["Settings", Literal["auto", "ui"]] = "auto",
        split: Optional[str] = None,
        subset: Optional[str] = None,
        **kwargs: Any,
    ) -> Union["Dataset", str]:
        """Loads a `Dataset` from the Hugging Face Hub.

        Parameters:
            repo_id: the ID of the Hugging Face Hub repo to load the `Dataset` from.
            name (str, optional): The name to assign to the new dataset. Defaults to None and the dataset's source name is used, unless it already exists, in which case a unique UUID is appended.
            workspace (Union[Workspace, str], optional): The workspace to import the dataset to. Defaults to None and default workspace is used.
            client: the client to use to load the `Dataset`. If not provided, the default client will be used.
            with_records: whether to load the records from the Hugging Face dataset. Defaults to `True`.
            settings: the settings to use to load the `Dataset`. If settings are "ui", a URL to configure the settings
                through argilla will be returned. If settings are "auto",
                the settings will be inferred from the `Features` of the dataset on the hub. Defaults to "auto".
            split: the split to load from the Hugging Face dataset. If not provided, the first split will be loaded.
            subset: the subset to load from the Hugging Face dataset. If not provided, the first subset will be loaded.
            **kwargs: the kwargs to pass to `datasets.Dataset.load_from_hub`.

        Returns:
            A `Dataset` loaded from the Hugging Face Hub.
        """
        from argilla.settings import Settings
        from datasets import load_dataset
        from huggingface_hub import snapshot_download

        if name is None:
            name = repo_id

        if settings == "ui":
            return cls._run_settings_ui(
                repo_id=repo_id,
                subset=subset,
                split=split,
                client=client,
            )

        elif isinstance(settings, Settings):
            dataset = cls(name=name, settings=settings)
            dataset.create()
        else:
            try:
                # download configuration files from the hub
                folder_path = snapshot_download(
                    repo_id=repo_id,
                    repo_type="dataset",
                    allow_patterns=cls._DEFAULT_CONFIGURATION_FILES,
                    token=kwargs.get("token"),
                )

                dataset = cls.from_disk(
                    path=folder_path, workspace=workspace, name=name, client=client, with_records=with_records
                )
            except ImportDatasetError:
                from argilla import Settings

                settings = Settings.from_hub(repo_id=repo_id, subset=subset)
                dataset = cls.from_hub(
                    repo_id=repo_id,
                    name=name,
                    workspace=workspace,
                    client=client,
                    with_records=with_records,
                    settings=settings,
                    split=split,
                    subset=subset,
                    **kwargs,
                )
                return dataset

        if with_records:
            try:
                hf_dataset = load_dataset(
                    path=repo_id,
                    split=split,
                    name=subset,
                    **kwargs,
                )  # type: ignore
                hf_dataset = cls._get_dataset_split(hf_dataset=hf_dataset, split=split, **kwargs)
                cls._log_dataset_records(hf_dataset=hf_dataset, dataset=dataset)
            except EmptyDatasetError:
                warnings.warn(
                    message="Trying to load a dataset `with_records=True` but dataset does not contain any records.",
                    category=UserWarning,
                )

        return dataset

    @staticmethod
    def _log_dataset_records(hf_dataset: "HFDataset", dataset: "Dataset"):
        """This method extracts the responses from a Hugging Face dataset and returns a list of `Record` objects"""
        # Identify columns that columns that contain responses
        responses_columns = [col for col in hf_dataset.column_names if ".responses" in col]
        response_questions = defaultdict(dict)
        user_ids = {}
        for col in responses_columns:
            question_name = col.split(".")[0]
            if col.endswith("users"):
                response_questions[question_name]["users"] = hf_dataset[col]
                user_ids.update({UUID(user_id): UUID(user_id) for user_id in set(sum(hf_dataset[col], []))})
            elif col.endswith("responses"):
                response_questions[question_name]["responses"] = hf_dataset[col]
            elif col.endswith("status"):
                response_questions[question_name]["status"] = hf_dataset[col]

        # Check if all user ids are known to this Argilla client
        known_users_ids = [user.id for user in dataset._client.users]
        unknown_user_ids = set(user_ids.keys()) - set(known_users_ids)
        my_user = dataset._client.me
        if len(unknown_user_ids) > 1:
            warnings.warn(
                message=f"""Found unknown user ids in dataset repo: {unknown_user_ids}.
                    Assigning first response for each record to current user ({my_user.username}) and discarding the rest."""
            )
        for unknown_user_id in unknown_user_ids:
            user_ids[unknown_user_id] = my_user.id

        # Create a mapper to map the Hugging Face dataset to a Record object
        mapping = {col: col for col in hf_dataset.column_names if ".suggestion" in col}
        mapper = IngestedRecordMapper(dataset=dataset, mapping=mapping, user_id=my_user.id)

        # Extract responses and create Record objects
        records = []
        hf_dataset = HFDatasetsIO.to_argilla(hf_dataset=hf_dataset, mapper=mapper)
        for idx, row in enumerate(hf_dataset):
            record = mapper(row)
            for question_name, values in response_questions.items():
                response_values = values["responses"][idx]
                response_users = values["users"][idx]
                response_status = values["status"][idx]
                for value, user_id, status in zip(response_values, response_users, response_status):
                    user_id = user_ids[UUID(user_id)]
                    if user_id in response_users:
                        continue
                    response_users[user_id] = True
                    response = Response(
                        user_id=user_id,
                        question_name=question_name,
                        value=value,
                        status=status,
                    )
                    record.responses.add(response)
            records.append(record)

        try:
            dataset.records.log(records=records)
        except (RecordsIngestionError, UnprocessableEntityError) as e:
            raise SettingsError(
                message=f"Failed to load records from Hugging Face dataset. Defined settings do not match dataset schema. Hugging face dataset features: {hf_dataset.features}. Argilla dataset settings : {dataset.settings}"
            ) from e

    @staticmethod
    def _get_dataset_split(hf_dataset: "HFDataset", split: Optional[str] = None, **kwargs: Dict) -> "HFDataset":
        """Get a single dataset from a Hugging Face dataset.

        Parameters:
            hf_dataset (HFDataset): The Hugging Face dataset to get a single dataset from.

        Returns:
            HFDataset: The single dataset.
        """

        if isinstance(hf_dataset, DatasetDict) and split is None:
            split = next(iter(hf_dataset.keys()))
            if len(hf_dataset.keys()) > 1:
                warnings.warn(
                    message=f"Multiple splits found in Hugging Face dataset. Using the first split: {split}. "
                    f"Available splits are: {', '.join(hf_dataset.keys())}."
                )
            hf_dataset = hf_dataset[split]
        return hf_dataset

    @staticmethod
    def _get_sample_hf_record(hf_dataset: "HFDataset") -> Dict:
        """Get a sample record from a Hugging Face dataset.

        Parameters:
            hf_dataset (HFDataset): The Hugging Face dataset to get a sample record from.

        Returns:
            Dict: The sample record.
        """

        if hf_dataset:
            sample_huggingface_record = {}
            for key, value in hf_dataset[0].items():
                try:
                    json.dumps(value)
                    sample_huggingface_record[key] = value
                except TypeError:
                    if isinstance(value, Image.Image):
                        sample_huggingface_record[key] = pil_to_data_uri(value)
                    else:
                        sample_huggingface_record[key] = "Record value is not serializable"
            return sample_huggingface_record
