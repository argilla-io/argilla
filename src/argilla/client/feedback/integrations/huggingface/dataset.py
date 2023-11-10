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

import json
import logging
import tempfile
import warnings
from typing import TYPE_CHECKING, Any, Optional, Type, Union

from packaging.version import parse as parse_version
from tqdm import trange

from argilla.client.feedback.constants import FIELD_TYPE_TO_PYTHON_TYPE
from argilla.client.feedback.schemas.enums import QuestionTypes
from argilla.client.feedback.schemas.records import FeedbackRecord
from argilla.client.feedback.schemas.remote.records import RemoteFeedbackRecord
from argilla.utils.dependency import requires_dependencies

if TYPE_CHECKING:
    from datasets import Dataset

    from argilla.client.feedback.dataset.local.dataset import FeedbackDataset
    from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset

_LOGGER = logging.getLogger(__name__)


class HuggingFaceDatasetMixin:
    @staticmethod
    @requires_dependencies("datasets")
    def _huggingface_format(dataset: Union["FeedbackDataset", "RemoteFeedbackDataset"]) -> "Dataset":
        """Formats either a `FeedbackDataset` or a `RemoteFeedbackDataset` as a `datasets.Dataset` object.

        Args:
            dataset: The `FeedbackDataset` or `RemoteFeedbackDataset` to format as `datasets.Dataset`.

        Returns:
            The records from the dataset formatted as a `datasets.Dataset` object, including the fields,
            questions, and metadata_properties formatted as `datasets.Features`.

        Examples:
            >>> from argilla.client.feedback.integrations.dataset import HuggingFaceDatasetMixin
            >>> dataset = FeedbackDataset(...) or RemoteFeedbackDataset(...)
            >>> huggingface_dataset = HuggingFaceDatasetMixin._huggingface_format(dataset)
        """
        from datasets import Dataset, Features, Sequence, Value

        hf_dataset, hf_features = {}, {}

        for field in dataset.fields:
            if field.type not in FIELD_TYPE_TO_PYTHON_TYPE.keys():
                raise ValueError(
                    f"Field {field.name} has an unsupported type: {field.type}, for the moment"
                    f" only the following types are supported: {list(FIELD_TYPE_TO_PYTHON_TYPE.keys())}"
                )
            hf_features[field.name] = Value(dtype="string", id="field")
            if field.name not in hf_dataset:
                hf_dataset[field.name] = []

        for question in dataset.questions:
            if question.type in [QuestionTypes.text, QuestionTypes.label_selection]:
                value = Value(dtype="string", id="question")
            elif question.type == QuestionTypes.rating:
                value = Value(dtype="int32", id="question")
            elif question.type == QuestionTypes.ranking:
                value = Sequence({"rank": Value(dtype="uint8"), "value": Value(dtype="string")}, id="question")
            elif question.type in QuestionTypes.multi_label_selection:
                value = Sequence(Value(dtype="string"), id="question")
            else:
                raise ValueError(
                    f"Question {question.name} is of type `{question.type}`,"
                    " for the moment only the following question types are supported:"
                    f" `{'`, `'.join([arg.value for arg in QuestionTypes])}`."
                )

            hf_features[question.name] = [
                {
                    "user_id": Value(dtype="string", id="question"),
                    "value": value,
                    "status": Value(dtype="string", id="question"),
                }
            ]
            if question.name not in hf_dataset:
                hf_dataset[question.name] = []

            value.id = "suggestion"
            hf_features[f"{question.name}-suggestion"] = value
            if f"{question.name}-suggestion" not in hf_dataset:
                hf_dataset[f"{question.name}-suggestion"] = []

            hf_features[f"{question.name}-suggestion-metadata"] = {
                "type": Value(dtype="string", id="suggestion-metadata"),
                "score": Value(dtype="float32", id="suggestion-metadata"),
                "agent": Value(dtype="string", id="suggestion-metadata"),
            }
            if f"{question.name}-suggestion-metadata" not in hf_dataset:
                hf_dataset[f"{question.name}-suggestion-metadata"] = []

        hf_features["external_id"] = Value(dtype="string", id="external_id")
        hf_dataset["external_id"] = []

        hf_features["metadata"] = Value(dtype="string", id="metadata")
        hf_dataset["metadata"] = []

        vectors_settings = dataset.vectors_settings
        if vectors_settings:
            hf_features["vectors"] = {}
            for vector_settings in vectors_settings:
                hf_features["vectors"].update({vector_settings.name: Sequence(Value(dtype="float32"), id="vectors")})
            hf_dataset["vectors"] = []

        for record in dataset.records:
            for field in dataset.fields:
                hf_dataset[field.name].append(record.fields.get(field.name, None))
            for question in dataset.questions:
                if not record.responses:
                    hf_dataset[question.name].append([])
                else:
                    responses = []
                    for response in record.responses:
                        if question.name not in response.values:
                            continue
                        formatted_response = {
                            "user_id": response.user_id,
                            "value": None,
                            "status": response.status.value if hasattr(response.status, "value") else response.status,
                        }
                        if question.type == QuestionTypes.ranking:
                            value = [r.dict() for r in response.values[question.name].value]
                        else:
                            value = response.values[question.name].value
                        formatted_response["value"] = value
                        responses.append(formatted_response)
                    hf_dataset[question.name].append(responses)

                suggestion_value, suggestion_metadata = None, {"type": None, "score": None, "agent": None}
                if record.suggestions:
                    for suggestion in record.suggestions:
                        if question.name == suggestion.question_name:
                            suggestion_value = suggestion.value
                            suggestion_metadata = {
                                "type": suggestion.type,
                                "score": suggestion.score,
                                "agent": suggestion.agent,
                            }
                            break
                hf_dataset[f"{question.name}-suggestion"].append(suggestion_value)
                hf_dataset[f"{question.name}-suggestion-metadata"].append(suggestion_metadata)

            hf_dataset["metadata"].append(json.dumps(record.metadata) if record.metadata else {})
            hf_dataset["external_id"].append(record.external_id or None)

            if vectors_settings:
                vectors = {}
                for vector_settings in vectors_settings:
                    vectors.update({vector_settings.name: record.vectors.get(vector_settings.name, None)})
                hf_dataset["vectors"].append(vectors)

        return Dataset.from_dict(hf_dataset, features=Features(hf_features))

    @requires_dependencies(["huggingface_hub", "datasets"])
    def push_to_huggingface(
        self: "FeedbackDataset",
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
            repo_id: the ID of the Hugging Face Hub repo to push the `FeedbackDataset` to.
            generate_card: whether to generate a dataset card for the `FeedbackDataset` in the Hugging Face Hub. Defaults
                to `True`.
            *args: the args to pass to `datasets.Dataset.push_to_hub`.
            **kwargs: the kwargs to pass to `datasets.Dataset.push_to_hub`.
        """
        import huggingface_hub
        from huggingface_hub import HfApi

        # https://github.com/argilla-io/argilla/issues/3468
        from argilla.client.feedback.config import DatasetConfig

        if parse_version(huggingface_hub.__version__) < parse_version("0.14.0"):
            _LOGGER.warning(
                "Recommended `huggingface_hub` version is 0.14.0 or higher, and you have"
                f" {huggingface_hub.__version__}, so in case you have any issue when pushing the dataset to the"
                " Hugging Face Hub upgrade it as `pip install huggingface_hub --upgrade`."
            )

        if len(self) < 1:
            raise ValueError(
                "Cannot push an empty `rg.FeedbackDataset` to the Hugging Face Hub, please make sure to add at"
                " least one record, via the method `add_records`."
            )

        hfds = self.format_as("datasets")
        hfds.push_to_hub(repo_id, *args, **kwargs)

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(
                DatasetConfig(
                    fields=self.fields,
                    questions=self.questions,
                    guidelines=self.guidelines,
                    metadata_properties=self.metadata_properties or None,
                    allow_extra_metadata=self.allow_extra_metadata,
                    vectors_settings=self.vectors_settings or None,
                ).to_yaml()
            )
            f.flush()

            HfApi().upload_file(
                path_or_fileobj=f.name,
                path_in_repo="argilla.yaml",
                repo_id=repo_id,
                repo_type="dataset",
                token=kwargs.get("token"),
            )

        if generate_card:
            from huggingface_hub import DatasetCardData

            from argilla.client.feedback.integrations.huggingface.card import (
                ArgillaDatasetCard,
                size_categories_parser,
            )

            sample_argilla_record = self.records[0]
            sample_argilla_record = (
                sample_argilla_record.to_local()
                if isinstance(sample_argilla_record, RemoteFeedbackRecord)
                else sample_argilla_record
            )
            sample_huggingface_record = hfds[0]

            card = ArgillaDatasetCard.from_template(
                card_data=DatasetCardData(
                    size_categories=size_categories_parser(len(self.records)),
                    tags=["rlfh", "argilla", "human-feedback"],
                ),
                repo_id=repo_id,
                argilla_fields=self.fields,
                argilla_questions=self.questions,
                argilla_guidelines=self.guidelines or None,
                argilla_vectors_settings=self.vectors_settings or None,
                argilla_metadata_properties=self.metadata_properties,
                argilla_record=json.loads(sample_argilla_record.json()),
                huggingface_record=sample_huggingface_record,
            )
            card.push_to_hub(repo_id, repo_type="dataset", token=kwargs.get("token"))

    @classmethod
    @requires_dependencies(["huggingface_hub", "datasets"])
    def from_huggingface(
        cls: Type["FeedbackDataset"], repo_id: str, show_progress: bool = True, *args: Any, **kwargs: Any
    ) -> "FeedbackDataset":
        """Loads a `FeedbackDataset` from the Hugging Face Hub.

        Args:
            repo_id: the ID of the Hugging Face Hub repo to load the `FeedbackDataset` from.
            *args: the args to pass to `datasets.Dataset.load_from_hub`.
            **kwargs: the kwargs to pass to `datasets.Dataset.load_from_hub`.

        Returns:
            A `FeedbackDataset` loaded from the Hugging Face Hub.
        """
        import huggingface_hub
        from datasets import DatasetDict, load_dataset
        from huggingface_hub import hf_hub_download
        from huggingface_hub.utils import EntryNotFoundError

        # https://github.com/argilla-io/argilla/issues/3468
        from argilla.client.feedback.config import (
            DatasetConfig,
            DeprecatedDatasetConfig,
        )

        if parse_version(huggingface_hub.__version__) < parse_version("0.14.0"):
            _LOGGER.warning(
                "Recommended `huggingface_hub` version is 0.14.0 or higher, and you have"
                f" {huggingface_hub.__version__}, so in case you have any issue when pushing the dataset to the"
                " Hugging Face Hub upgrade it as `pip install huggingface_hub --upgrade`."
            )

        if "token" in kwargs:
            auth = kwargs.pop("token")
        elif "use_auth_token" in kwargs:
            auth = kwargs.pop("use_auth_token")
        else:
            auth = None

        hub_auth = (
            {"use_auth_token": auth}
            if parse_version(huggingface_hub.__version__) < parse_version("0.11.0")
            else {"token": auth}
        )

        try:
            config_path = hf_hub_download(
                repo_id=repo_id,
                filename="argilla.yaml",
                repo_type="dataset",
                **hub_auth,
            )
            with open(config_path, "r") as f:
                config = DatasetConfig.from_yaml(f.read())
                dataset = cls(
                    fields=config.fields,
                    questions=config.questions,
                    guidelines=config.guidelines,
                    metadata_properties=config.metadata_properties,
                    allow_extra_metadata=config.allow_extra_metadata,
                    vectors_settings=config.vectors_settings,
                )
        except EntryNotFoundError:
            # TODO(alvarobartt): here for backwards compatibility, last used in 1.12.0
            warnings.warn(
                "No `argilla.yaml` file found in the Hugging Face Hub repository, which"
                " means that the `DatasetConfig` was dumped using Argilla 1.12.0 or"
                " lower, and the `argilla.yaml` file was not generated. Please consider"
                " re-dumping the `DatasetConfig` using Argilla 1.13.0 or higher, or"
                " manually create the `argilla.yaml` file in the Hugging Face Hub.",
                UserWarning,
            )
            config_path = hf_hub_download(
                repo_id=repo_id,
                filename="argilla.cfg",
                repo_type="dataset",
                **hub_auth,
            )
            with open(config_path, "r") as f:
                config = DeprecatedDatasetConfig.from_json(f.read())
                dataset = cls(fields=config.fields, questions=config.questions, guidelines=config.guidelines)
        except Exception as e:
            raise FileNotFoundError(
                "Neither `argilla.yaml` nor `argilla.cfg` files were found in the"
                " Hugging Face Hub repository. Please make sure to dump the `DatasetConfig`"
                " using `FeedbackDataset.push_to_huggingface` to automatically upload"
                " the `DatasetConfig` as `argilla.yaml` to the Hugging Face Hub."
            ) from e

        hfds = load_dataset(repo_id, token=auth, *args, **kwargs)  # use_auth_token is deprecated
        if isinstance(hfds, DatasetDict) and "split" not in kwargs:
            if len(hfds.keys()) > 1:
                raise ValueError(
                    "Only one dataset can be loaded at a time, use `split` to select a split, available splits"
                    f" are: {', '.join(hfds.keys())}."
                )
            hfds = hfds[list(hfds.keys())[0]]

        records = []
        for index in trange(0, len(hfds), desc="Parsing records", disable=not show_progress):
            responses = {}
            suggestions = []
            user_without_id = False
            for question in dataset.questions:
                if hfds[index][question.name] is not None and len(hfds[index][question.name]) > 0:
                    if (
                        len(
                            [None for response in hfds[index][question.name] if response["user_id"] is None]
                            if isinstance(hfds[index][question.name], list)
                            else [None for user_id in hfds[index][question.name]["user_id"] if user_id is None]
                        )
                        > 1
                    ):
                        warnings.warn(
                            "Found more than one user without ID in the dataset, so just the"
                            " responses for the first user without ID will be used, the rest"
                            " will be discarded."
                        )

                    # Here for backwards compatibility
                    original_responses = []
                    if isinstance(hfds[index][question.name], list):
                        original_responses = hfds[index][question.name]
                    else:
                        for user_id, value, status in zip(
                            hfds[index][question.name]["user_id"],
                            hfds[index][question.name]["value"],
                            hfds[index][question.name]["status"],
                        ):
                            original_responses.append({"user_id": user_id, "value": value, "status": status})

                    user_without_id_response = False
                    for response in original_responses:
                        if user_without_id_response:
                            continue
                        user_id = response["user_id"]
                        status = response["status"]
                        if user_id is None:
                            if not user_without_id:
                                user_without_id = True
                                responses["user_without_id"] = {
                                    "user_id": user_id,
                                    "status": status,
                                    "values": {},
                                }
                                user_without_id_response = True
                        if user_id is not None and user_id not in responses:
                            responses[user_id] = {
                                "user_id": user_id,
                                "status": status,
                                "values": {},
                            }
                        value = response["value"]
                        if value is not None:
                            if question.type == QuestionTypes.ranking:
                                value = [{"rank": r, "value": v} for r, v in zip(value["rank"], value["value"])]
                            responses[user_id or "user_without_id"]["values"].update({question.name: {"value": value}})

                # First if-condition is here for backwards compatibility
                if (
                    f"{question.name}-suggestion" in hfds[index]
                    and hfds[index][f"{question.name}-suggestion"] is not None
                ):
                    suggestion = {
                        "question_name": question.name,
                        "value": hfds[index][f"{question.name}-suggestion"],
                    }
                    if hfds[index][f"{question.name}-suggestion-metadata"] is not None:
                        suggestion.update(hfds[index][f"{question.name}-suggestion-metadata"])
                    suggestions.append(suggestion)

            metadata = None
            if "metadata" in hfds[index] and hfds[index]["metadata"] is not None:
                metadata = json.loads(hfds[index]["metadata"])

            vectors = {}
            if "vectors" in hfds[index] and hfds[index]["vectors"]:
                for vector_settings in dataset.vectors_settings:
                    if hfds[index]["vectors"].get(vector_settings.name, None) is not None:
                        vectors.update({vector_settings.name: hfds[index]["vectors"][vector_settings.name]})

            records.append(
                FeedbackRecord(
                    fields={field.name: hfds[index][field.name] for field in dataset.fields},
                    metadata=metadata or {},
                    responses=list(responses.values()) or [],
                    suggestions=[suggestion for suggestion in suggestions if suggestion["value"] is not None] or [],
                    vectors=vectors or {},
                    external_id=hfds[index]["external_id"],
                )
            )
        del hfds

        dataset.add_records(records)

        return dataset
