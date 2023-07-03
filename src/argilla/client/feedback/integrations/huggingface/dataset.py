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
from typing import TYPE_CHECKING, Any, Optional, Type, TypeVar

import huggingface_hub
from datasets import Dataset, DatasetDict, Features, Sequence, Value, load_dataset
from huggingface_hub import DatasetCardData, HfApi, hf_hub_download
from huggingface_hub.utils import EntryNotFoundError
from packaging.version import parse as parse_version

from argilla.client.feedback.config import DatasetConfig
from argilla.client.feedback.constants import FIELD_TYPE_TO_PYTHON_TYPE
from argilla.client.feedback.schemas import FeedbackRecord
from argilla.client.feedback.typing import AllowedQuestionTypes

if TYPE_CHECKING:
    from argilla.client.feedback.dataset import FeedbackDataset

_LOGGER = logging.getLogger(__name__)

T = TypeVar("T", bound="FeedbackDataset")


class HuggingFaceDatasetMixIn:
    @staticmethod
    def _huggingface_format(feedback_dataset: T) -> "Dataset":
        """Formats a `FeedbackDataset` as a `datasets.Dataset` object.

        Returns:
            The `FeedbackDataset.records` formatted as a `datasets.Dataset` object,
            including the `FeedbackDataset.fields` and `FeedbackDataset.questions` as
            `datasets.Features`.

        Examples:
            >>> import argilla as rg
            >>> rg.init(...)
            >>> dataset = rg.FeedbackDataset.from_argilla(name="my-dataset")
            >>> huggingface_dataset = rg.HuggingFaceDatasetMixIn.set_format(dataset)
        """
        dataset, features = {}, {}

        for field in feedback_dataset.fields:
            if field.settings["type"] not in FIELD_TYPE_TO_PYTHON_TYPE.keys():
                raise ValueError(
                    f"Field {field.name} has an unsupported type: {field.settings['type']}, for the moment"
                    f" only the following types are supported: {list(FIELD_TYPE_TO_PYTHON_TYPE.keys())}"
                )
            features[field.name] = Value(dtype="string", id="field")
            if field.name not in dataset:
                dataset[field.name] = []

        for question in feedback_dataset.questions:
            if question.settings["type"] in ["text", "label_selection"]:
                value = Value(dtype="string")
            elif question.settings["type"] == "rating":
                value = Value(dtype="int32")
            elif question.settings["type"] == "ranking":
                value = Sequence({"rank": Value(dtype="uint8"), "value": Value(dtype="string")})
            elif question.settings["type"] in "multi_label_selection":
                value = Sequence(Value(dtype="string"))
            else:
                raise ValueError(
                    f"Question {question.name} is of type `{type(question).__name__}`,"
                    " for the moment only the following question types are supported:"
                    f" `{'`, `'.join([arg.__name__ for arg in AllowedQuestionTypes.__args__])}`."
                )

            features[question.name] = Sequence(
                {
                    "user_id": Value(dtype="string"),
                    "value": value,
                    "status": Value(dtype="string"),
                },
                id="question",
            )
            if question.name not in dataset:
                dataset[question.name] = []

        features["external_id"] = Value(dtype="string", id="external_id")
        dataset["external_id"] = []

        dataset["metadata"] = []

        for record in feedback_dataset.records:
            for field in feedback_dataset.fields:
                dataset[field.name].append(record.fields[field.name])
            for question in feedback_dataset.questions:
                if not record.responses:
                    dataset[question.name].append(None)
                    continue
                responses = []
                for response in record.responses:
                    if question.name not in response.values:
                        responses.append(None)
                        continue
                    if question.settings["type"] == "ranking":
                        responses.append([r.dict() for r in response.values[question.name].value])
                    else:
                        responses.append(response.values[question.name].value)
                dataset[question.name].append(
                    {
                        "user_id": [r.user_id for r in record.responses],
                        "value": responses,
                        "status": [r.status for r in record.responses],
                    }
                )
            dataset["metadata"].append(json.dumps(record.metadata) if record.metadata else None)
            dataset["external_id"].append(record.external_id or None)

        if dataset.get("metadata", None) is not None:
            features["metadata"] = Value(dtype="string")

        return Dataset.from_dict(
            dataset,
            features=Features(features),
        )

    def _push_to_huggingface(
        self, feedback_dataset: T, repo_id: str, generate_card: Optional[bool] = True, *args, **kwargs
    ) -> None:
        """Pushes the `FeedbackDataset` to the HuggingFace Hub. If the dataset has been previously pushed to the
        HuggingFace Hub, it will be updated instead. Note that some params as `private` have no effect at all
        when a dataset is previously uploaded to the HuggingFace Hub.

        Args:
            repo_id: the ID of the HuggingFace Hub repo to push the `FeedbackDataset` to.
            generate_card: whether to generate a dataset card for the `FeedbackDataset` in the HuggingFace Hub. Defaults
                to `True`.
            *args: the args to pass to `datasets.Dataset.push_to_hub`.
            **kwargs: the kwargs to pass to `datasets.Dataset.push_to_hub`.
        """
        if parse_version(huggingface_hub.__version__) < parse_version("0.14.0"):
            _LOGGER.warning(
                "Recommended `huggingface_hub` version is 0.14.0 or higher, and you have"
                f" {huggingface_hub.__version__}, so in case you have any issue when pushing the dataset to the"
                " HuggingFace Hub upgrade it as `pip install huggingface_hub --upgrade`."
            )

        if len(self) < 1:
            raise ValueError(
                "Cannot push an empty `rg.FeedbackDataset` to the HuggingFace Hub, please make sure to add at"
                " least one record, via the method `add_records`."
            )

        hfds = self.format_as("datasets")
        hfds.push_to_hub(repo_id, *args, **kwargs)

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(
                DatasetConfig(
                    fields=feedback_dataset.fields,
                    questions=feedback_dataset.questions,
                    guidelines=feedback_dataset.guidelines,
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
            from argilla.client.feedback.integrations.huggingface.card import (
                ArgillaDatasetCard,
                size_categories_parser,
            )

            card = ArgillaDatasetCard.from_template(
                card_data=DatasetCardData(
                    size_categories=size_categories_parser(len(feedback_dataset.records)),
                    tags=["rlfh", "argilla", "human-feedback"],
                ),
                repo_id=repo_id,
                argilla_fields=feedback_dataset.fields,
                argilla_questions=feedback_dataset.questions,
                argilla_guidelines=feedback_dataset.guidelines,
                argilla_record=json.loads(feedback_dataset.records[0].json()),
                huggingface_record=hfds[0],
            )
            card.push_to_hub(repo_id, repo_type="dataset", token=kwargs.get("token"))

    @staticmethod
    def _from_huggingface(cls: Type[T], repo_id: str, *args: Any, **kwargs: Any) -> T:
        """Loads a `FeedbackDataset` from the HuggingFace Hub.

        Args:
            repo_id: the ID of the HuggingFace Hub repo to load the `FeedbackDataset` from.
            *args: the args to pass to `datasets.Dataset.load_from_hub`.
            **kwargs: the kwargs to pass to `datasets.Dataset.load_from_hub`.

        Returns:
            A `FeedbackDataset` loaded from the HuggingFace Hub.
        """
        if parse_version(huggingface_hub.__version__) < parse_version("0.14.0"):
            _LOGGER.warning(
                "Recommended `huggingface_hub` version is 0.14.0 or higher, and you have"
                f" {huggingface_hub.__version__}, so in case you have any issue when pushing the dataset to the"
                " HuggingFace Hub upgrade it as `pip install huggingface_hub --upgrade`."
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
        except EntryNotFoundError:
            # TODO(alvarobartt): here for backwards compatibility, remove in 1.14.0
            warnings.warn(
                "No `argilla.yaml` file found in the HuggingFace Hub repository, which"
                " means that the `DatasetConfig` was dumped using Argilla 1.12.0 or"
                " lower, and the `argilla.yaml` file was not generated. Please consider"
                " re-dumping the `DatasetConfig` using Argilla 1.13.0 or higher, or"
                " manually create the `argilla.yaml` file in the HuggingFace Hub.",
                UserWarning,
            )
            config_path = hf_hub_download(
                repo_id=repo_id,
                filename="argilla.cfg",
                repo_type="dataset",
                **hub_auth,
            )
            with open(config_path, "r") as f:
                config = DatasetConfig.from_json(f.read())
        except Exception as e:
            raise FileNotFoundError(
                "Neither `argilla.yaml` nor `argilla.cfg` files were found in the"
                " HuggingFace Hub repository. Please make sure to dump the `DatasetConfig`"
                " using `FeedbackDataset.push_to_huggingface` to automatically upload"
                " the `DatasetConfig` as `argilla.yaml` to the HuggingFace Hub."
            )

        hfds = load_dataset(repo_id, use_auth_token=auth, *args, **kwargs)
        if isinstance(hfds, DatasetDict) and "split" not in kwargs:
            if len(hfds.keys()) > 1:
                raise ValueError(
                    "Only one dataset can be loaded at a time, use `split` to select a split, available splits"
                    f" are: {', '.join(hfds.keys())}."
                )
            hfds = hfds[list(hfds.keys())[0]]

        records = []
        for index in range(len(hfds)):
            responses = {}
            for question in config.questions:
                if hfds[index][question.name] is None or len(hfds[index][question.name]) < 1:
                    continue
                for user_id, value, status in zip(
                    hfds[index][question.name]["user_id"],
                    hfds[index][question.name]["value"],
                    hfds[index][question.name]["status"],
                ):
                    if user_id not in responses:
                        responses[user_id] = {
                            "user_id": user_id,
                            "status": status,
                            "values": {},
                        }
                    if question.settings["type"] == "ranking":
                        value = [{"rank": r, "value": v} for r, v in zip(value["rank"], value["value"])]
                    responses[user_id]["values"].update({question.name: {"value": value}})

            metadata = None
            if "metadata" in hfds[index] and hfds[index]["metadata"] is not None:
                metadata = json.loads(hfds[index]["metadata"])

            records.append(
                FeedbackRecord(
                    fields={field.name: hfds[index][field.name] for field in config.fields},
                    metadata=metadata,
                    responses=list(responses.values()) or None,
                    external_id=hfds[index]["external_id"],
                )
            )
        del hfds
        cls = cls(
            fields=config.fields,
            questions=config.questions,
            guidelines=config.guidelines,
        )
        cls.add_records(records)
        return cls
