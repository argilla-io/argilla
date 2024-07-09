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

import warnings
from collections import defaultdict
from tempfile import TemporaryDirectory
from typing import Any, Type, TYPE_CHECKING, Optional
from uuid import UUID

from argilla.records import Record
from argilla.responses import Response
from argilla._exceptions import NotFoundError

if TYPE_CHECKING:
    from argilla import Dataset


class HubImportExportMixin:
    _default_dataset_repo_dir_name = ".argilla"
    _default_configuration_files = ["settings.json", "dataset.json"]

    def to_hub(
        self: "Dataset",
        repo_id: str,
        generate_card: Optional[bool] = True,
        *args,
        **kwargs,
    ) -> None:
        """Pushes the `FeedbackDataset` to the Hugging Face Hub. If the dataset has been previously pushed to the
        Hugging Face Hub, it will be updated instead. Note that some params as `private` have no effect at all
        when a dataset is previously uploaded to the Hugging Face Hub.

        Args:
            dataset: the `FeedbackDataset` to push to the Hugging Face Hub.
            repo_id: the ID of the Hugging Face Hub repo to push the `Dataset` to.
            generate_card: whether to generate a dataset card for the `FeedbackDataset` in the Hugging Face Hub. Defaults
                to `True`.
            *args: the args to pass to `datasets.Dataset.push_to_hub`.
            **kwargs: the kwargs to pass to `datasets.Dataset.push_to_hub`.
        """

        from huggingface_hub import HfApi, DatasetCardData

        from argilla.datasets._export.card import (
            ArgillaDatasetCard,
            size_categories_parser,
        )

        hf_api = HfApi()

        hfds = self.records(with_vectors=True, with_responses=True, with_suggestions=True).to_datasets()
        hfds.push_to_hub(repo_id, *args, **kwargs)

        with TemporaryDirectory() as tmpdirname:
            self.to_disk(path=tmpdirname, include_records=False)
            hf_api.upload_folder(
                folder_path=tmpdirname,
                repo_id=repo_id,
                repo_type="dataset",
                token=kwargs.get("token"),
                path_in_repo=self._default_dataset_repo_dir_name,
            )

        if generate_card:
            sample_argilla_record = next(iter(self.records(with_suggestions=True, with_responses=True)))
            sample_huggingface_record = hfds[0]
            card = ArgillaDatasetCard.from_template(
                card_data=DatasetCardData(
                    size_categories=size_categories_parser(len(hfds)),
                    tags=["rlfh", "argilla", "human-feedback"],
                ),
                repo_id=repo_id,
                argilla_fields=self.settings.fields,
                argilla_questions=self.settings.questions,
                argilla_guidelines=self.settings.guidelines or None,
                argilla_vectors_settings=self.settings.vectors or None,
                argilla_metadata_properties=self.settings.metadata,
                argilla_record=sample_argilla_record.api_model().model_dump_json(),
                huggingface_record=sample_huggingface_record,
            )
            card.push_to_hub(repo_id, repo_type="dataset", token=kwargs.get("token"))

    @classmethod
    def from_hub(
        cls: Type["Dataset"],
        repo_id: str,
        workspace: Optional[Union["Workspace", str, UUID]] = None,
        client: Optional["Argilla"] = None,
        *args: Any,
        **kwargs: Any,
    ):
        """Loads a `FeedbackDataset` from the Hugging Face Hub.

        Args:
            repo_id: the ID of the Hugging Face Hub repo to load the `FeedbackDataset` from.
            *args: the args to pass to `datasets.Dataset.load_from_hub`.
            **kwargs: the kwargs to pass to `datasets.Dataset.load_from_hub`.

        Returns:
            A `FeedbackDataset` loaded from the Hugging Face Hub.
        """
        from datasets import DatasetDict, load_dataset, Dataset
        from huggingface_hub import hf_hub_download

        with TemporaryDirectory() as tmpdirname:
            for filename in cls._default_configuration_files:
                hf_hub_download(
                    repo_id=repo_id,
                    filename=filename,
                    repo_type="dataset",
                    local_dir=tmpdirname,
                )
            dataset = cls.from_disk(path=tmpdirname, target_workspace=workspace, client=client)
        hf_dataset: Dataset = load_dataset(path=repo_id, *args, **kwargs)  # type: ignore
        if isinstance(hf_dataset, DatasetDict) and "split" not in kwargs:
            if len(hf_dataset.keys()) > 1:
                raise ValueError(
                    "Only one dataset can be loaded at a time, use `split` to select a split, available splits"
                    f" are: {', '.join(hf_dataset.keys())}."
                )
            hf_dataset: Dataset = hf_dataset[list(hf_dataset.keys())[0]]
 
        dataset.create()
        cls._extract_suggestions(hf_dataset=hf_dataset, dataset=dataset)
        cls._extract_responses(hf_dataset=hf_dataset, dataset=dataset)
        return dataset

    @staticmethod
    def _extract_suggestions(hf_dataset, dataset) -> None:
        """ This method extracts the suggestions from a Hugging Face dataset and logs them as records. """
        mapping = {col: col for col in hf_dataset.column_names if ".suggestion" in col}
        dataset.records.log(records=hf_dataset, mapping=mapping)


    @staticmethod
    def _extract_responses(hf_dataset, dataset):
        """This method extracts the responses from a Hugging Face dataset and returns a list of `Record` objects"""

        # Identify columns that colunms that contain responses
        responses_columns = [col for col in hf_dataset.column_names if ".responses" in col]
        response_questions = defaultdict(dict)
        user_ids = {}
        for col in responses_columns:
            question_name = col.split(".")[0]
            if col.endswith("users"):
                response_questions[question_name]["users"] = hf_dataset[col]
                user_ids.update({user_id: user_id for user_id in hf_dataset[col]})
            else:
                response_questions[question_name]["responses"] = hf_dataset[col]

        # check that all response user ids are valid and replace if not
        for user_id in user_ids:
            try:
                dataset.client.users._api.get(user_id)
            except NotFoundError:
                warnings.warn(message=f"User {user_id} not found. Assigning responses to current user..")
                user_ids[user_id] = dataset.client.me.id

        # Extract responses and create Record objects
        records_with_responses = []
        for idx, row in enumerate(hf_dataset):
            responses = []
            row_id = row.pop("id")
            for question_name, values in response_questions.items():
                for value, user_id in zip(values["responses"][idx], values["users"][idx]):
                    response = Response(
                        user_id=user_ids[user_id],
                        question_name=question_name,
                        value=value,
                    )
                    responses.append(response)
            record = Record(
                id=row_id,
                responses=responses,
            )
            records_with_responses.append(record)
        dataset.records.log(records=records_with_responses)
