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

import logging
import textwrap
import warnings
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional, Tuple, Union

from argilla_v1.client.feedback.constants import FETCHING_BATCH_SIZE
from argilla_v1.client.feedback.dataset import helpers
from argilla_v1.client.feedback.dataset.base import FeedbackDatasetBase, R
from argilla_v1.client.feedback.dataset.local.mixins import ArgillaMixin, TaskTemplateMixin
from argilla_v1.client.feedback.dataset.mixins import MetricsMixin, UnificationMixin
from argilla_v1.client.feedback.integrations.huggingface.dataset import HuggingFaceDatasetMixin
from argilla_v1.client.feedback.schemas.enums import RecordSortField, SortOrder
from argilla_v1.client.feedback.schemas.records import FeedbackRecord
from argilla_v1.client.feedback.schemas.vector_settings import VectorSettings
from argilla_v1.client.feedback.training.schemas.base import (
    TrainingTaskForChatCompletion,
    TrainingTaskForDPO,
    TrainingTaskForPPO,
    TrainingTaskForQuestionAnswering,
    TrainingTaskForRM,
    TrainingTaskForSentenceSimilarity,
    TrainingTaskForSFT,
    TrainingTaskForTextClassification,
    TrainingTaskTypes,
)
from argilla_v1.client.models import Framework

if TYPE_CHECKING:
    from argilla_v1.client.feedback.schemas.types import (
        AllowedFieldTypes,
        AllowedMetadataPropertyTypes,
        AllowedQuestionTypes,
    )


_LOGGER = logging.getLogger(__name__)


class FeedbackDataset(
    ArgillaMixin,
    HuggingFaceDatasetMixin,
    FeedbackDatasetBase[FeedbackRecord],
    TaskTemplateMixin,
    MetricsMixin,
    UnificationMixin,
):
    def __init__(
        self,
        *,
        fields: List["AllowedFieldTypes"],
        questions: List["AllowedQuestionTypes"],
        metadata_properties: Optional[List["AllowedMetadataPropertyTypes"]] = None,
        vectors_settings: Optional[List[VectorSettings]] = None,
        guidelines: Optional[str] = None,
        allow_extra_metadata: bool = True,
    ) -> None:
        """Initializes a `FeedbackDataset` instance locally.

        Args:
            fields: contains the fields that will define the schema of the records in the dataset.
            questions: contains the questions that will be used to annotate the dataset.
            metadata_properties: contains the metadata properties that will be indexed
                and could be used to filter the dataset. Defaults to `None`.
            vectors_settings: contains the vectors settings that will define the configuration
                of the vectors associated to the records in the dataset and that would
                allow to perform vector search. Defaults to `None`.
            guidelines: contains the guidelines for annotating the dataset. Defaults to `None`.
            allow_extra_metadata: whether to allow extra metadata that has not been defined
                as a metadata property in the records. Defaults to `True`.

        Raises:
            TypeError: if `fields` is not a list of `FieldSchema`.
            ValueError: if `fields` does not contain at least one required field.
            TypeError: if `questions` is not a list of `TextQuestion`, `RatingQuestion`,
                `LabelQuestion`, and/or `MultiLabelQuestion`.
            ValueError: if `questions` does not contain at least one required question.
            TypeError: if `guidelines` is not None and not a string.
            ValueError: if `guidelines` is an empty string.

        Examples:
            >>> import argilla_v1 as rg
            >>> rg.init(api_url="...", api_key="...")
            >>> dataset = rg.FeedbackDataset(
            ...     fields=[
            ...         rg.TextField(name="text", required=True),
            ...         rg.TextField(name="label", required=True),
            ...     ],
            ...     questions=[
            ...         rg.TextQuestion(
            ...             name="question-1",
            ...             description="This is the first question",
            ...             required=True,
            ...         ),
            ...         rg.RatingQuestion(
            ...             name="question-2",
            ...             description="This is the second question",
            ...             required=True,
            ...             values=[1, 2, 3, 4, 5],
            ...         ),
            ...         rg.LabelQuestion(
            ...             name="question-3",
            ...             description="This is the third question",
            ...             required=True,
            ...             labels=["positive", "negative"],
            ...         ),
            ...         rg.MultiLabelQuestion(
            ...             name="question-4",
            ...             description="This is the fourth question",
            ...             required=True,
            ...             labels=["category-1", "category-2", "category-3"],
            ...         ),
            ...     ],
            ...     metadata_properties=[
            ...         rg.TermsMetadataProperty(
            ...             name="metadata-property-1",
            ...             values=["a", "b", "c"]
            ...         ),
            ...         rg.IntegerMetadataProperty(
            ...             name="metadata-property-2",
            ...             gt=0,
            ...             lt=10,
            ...         ),
            ...         rg.FloatMetadataProperty(
            ...             name="metadata-property-2",
            ...             gt=-10.0,
            ...             lt=10.0,
            ...         ),
            ...     ],
            ...     guidelines="These are the annotation guidelines.",
            ... )
        """

        helpers.validate_fields(fields)
        helpers.validate_questions(questions)
        helpers.validate_metadata_properties(metadata_properties)

        if guidelines is not None:
            if not isinstance(guidelines, str):
                raise TypeError(
                    f"Expected `guidelines` to be either None (default) or a string, got {type(guidelines)} instead."
                )
            if len(guidelines) < 1:
                raise ValueError(
                    "Expected `guidelines` to be either None (default) or a non-empty string, minimum length is 1."
                )

        self._fields = fields or []
        self._questions = questions or []
        self._metadata_properties = metadata_properties or []
        self._guidelines = guidelines
        self._allow_extra_metadata = allow_extra_metadata

        if vectors_settings:
            self._vectors_settings = {vector_setting.name: vector_setting for vector_setting in vectors_settings}
        else:
            self._vectors_settings: Dict[str, VectorSettings] = {}
        self._records = []

    @property
    def guidelines(self) -> Optional[str]:
        return self._guidelines

    @property
    def allow_extra_metadata(self) -> bool:
        return self._allow_extra_metadata

    @property
    def fields(self) -> Union[List["AllowedFieldTypes"]]:
        return self._fields

    @property
    def questions(self) -> Union[List["AllowedQuestionTypes"]]:
        return self._questions

    @property
    def metadata_properties(
        self,
    ) -> Union[List["AllowedMetadataPropertyTypes"]]:
        return self._metadata_properties

    @property
    def vectors_settings(self) -> List["VectorSettings"]:
        """Returns the vector settings of the dataset."""
        return [v for v in self._vectors_settings.values()]

    @property
    def records(self) -> List["FeedbackRecord"]:
        """Returns the records in the dataset."""
        return self._records

    def __repr__(self) -> str:
        """Returns a string representation of the dataset."""
        indent = "   "
        return (
            "FeedbackDataset("
            + textwrap.indent(f"\nfields={self.fields}", indent)
            + textwrap.indent(f"\nquestions={self.questions}", indent)
            + textwrap.indent(f"\nguidelines={self.guidelines})", indent)
            + textwrap.indent(f"\nmetadata_properties={self.metadata_properties})", indent)
            + textwrap.indent(f"\nvectors_settings={self.vectors_settings})", indent)
            + "\n)"
        )

    def __len__(self) -> int:
        """Returns the number of records in the dataset."""
        return len(self._records)

    def __getitem__(self, key: Union[slice, int]) -> Union["FeedbackRecord", List["FeedbackRecord"]]:
        """Returns the record(s) at the given index(es).

        Args:
            key: the index(es) of the record(s) to return. Can either be a single index or a slice.

        Returns:
            Either the record of the given index, or a list with the records at the given indexes.
        """
        if len(self._records) < 1:
            raise RuntimeError(
                "In order to get items from `FeedbackDataset` you need to add them first" " with `add_records`."
            )
        if isinstance(key, int) and len(self._records) < key:
            raise IndexError(f"This dataset contains {len(self)} records, so index {key} is out of range.")
        return self._records[key]

    def iter(self, batch_size: Optional[int] = FETCHING_BATCH_SIZE) -> Iterator[List["FeedbackRecord"]]:
        """Returns an iterator over the records in the dataset.

        Args:
            batch_size: the size of the batches to return. Defaults to 100.
        """
        for i in range(0, len(self._records), batch_size):
            yield self._records[i : i + batch_size]

    def add_records(
        self, records: Union["FeedbackRecord", Dict[str, Any], List[Union["FeedbackRecord", Dict[str, Any]]]]
    ) -> None:
        """Adds the given records to the dataset, and stores them locally. If you are
        planning to push those to Argilla, you will need to call `push_to_argilla` afterwards,
        to both create the dataset in Argilla and push the records to it. Then, from a
        `FeedbackDataset` pushed to Argilla, you'll just need to call `add_records` and
        those will be automatically uploaded to Argilla.

        Args:
            records: can be a single `FeedbackRecord`, a list of `FeedbackRecord`,
                a single dictionary, or a list of dictionaries. If a dictionary is provided,
                it will be converted to a `FeedbackRecord` internally.

        Raises:
            ValueError: if the given records are an empty list.
            ValueError: if the given records are neither: `FeedbackRecord`, list of `FeedbackRecord`,
                list of dictionaries as a record or dictionary as a record.
            ValueError: if the given records do not match the expected schema.
        """
        records = helpers.normalize_records(records)
        helpers.validate_dataset_records(self, records)

        if len(self._records) > 0:
            self._records += records
        else:
            self._records = records

    def add_metadata_property(
        self, metadata_property: "AllowedMetadataPropertyTypes"
    ) -> "AllowedMetadataPropertyTypes":
        """Adds the given metadata property to the dataset.

        Args:
            metadata_property: the metadata property to add.

        Returns:
            The metadata property that was added.

        Raises:
            TypeError: if `metadata_property` is not a `MetadataPropertySchema`.
            ValueError: if `metadata_property` is already in the dataset.
        """
        self._unique_metadata_property(metadata_property)
        self._metadata_properties.append(metadata_property)
        return metadata_property

    def add_vector_settings(self, vector_settings: VectorSettings) -> VectorSettings:
        if self._vectors_settings.get(vector_settings.name):
            raise ValueError(f"Vector settings with name '{vector_settings.name}' already exists in the dataset.")

        self._vectors_settings[vector_settings.name] = vector_settings
        return vector_settings

    def update_vectors_settings(self, vectors_settings: Union[VectorSettings, List[VectorSettings]]) -> None:
        """Does nothing because the `vector_settings` are updated automatically for
        `FeedbackDataset` datasets when assigning their updateable attributes to a new value.
        """
        warnings.warn(
            "`update_vectors_settings` method is not supported for `FeedbackDataset` datasets"
            " unless its pushed to Argilla i.e. `RemoteFeedbackDataset`. This is because the"
            " `vector_settings` updates are already applied via assignment if any. So,"
            " this method is not required locally.",
            UserWarning,
            stacklevel=1,
        )

    def delete_vectors_settings(
        self, vectors_settings: Union[str, List[str]]
    ) -> Union[VectorSettings, List[VectorSettings]]:
        """Deletes the given vector settings from the dataset.

        Args:
            vectors_settings: the name/s of the vector settings to delete.

        Returns:
            The vector settings that were deleted.

        Raises:
            ValueError: if the provided `vectors_settings` is/are not in the dataset.
        """
        if isinstance(vectors_settings, str):
            vectors_settings = [vectors_settings]

        if not self.vectors_settings:
            raise ValueError(
                "The current `FeedbackDataset` does not contain any `vectors_settings` defined, so"
                " none can be deleted."
            )

        if not all(vector_setting in self._vectors_settings.keys() for vector_setting in vectors_settings):
            raise ValueError(
                f"Invalid `vectors_settings={vectors_settings}` provided. It cannot be"
                " deleted because it does not exist, make sure you delete just existing `vectors_settings`"
                " meaning that the name matches any of the existing `vectors_settings` if any. Current"
                f" `vectors_settings` are: '{', '.join(self._vectors_settings.keys())}'."
            )

        deleted_vectors_settings = []
        for vector_setting in vectors_settings:
            deleted_vectors_settings.append(self._vectors_settings.pop(vector_setting))
        return deleted_vectors_settings if len(deleted_vectors_settings) > 1 else deleted_vectors_settings[0]

    def update_metadata_properties(
        self,
        metadata_properties: Union["AllowedMetadataPropertyTypes", List["AllowedMetadataPropertyTypes"]],
    ) -> None:
        """Does nothing because the `metadata_properties` are updated automatically for
        `FeedbackDataset` datasets when assigning their updateable attributes to a new value.
        """
        warnings.warn(
            "`update_metadata_properties` method is not supported for `FeedbackDataset` datasets"
            " unless its pushed to Argilla i.e. `RemoteFeedbackDataset`. This is because the"
            " `metadata_properties` updates are already applied via assignment if any. So,"
            " this method is not required locally.",
            UserWarning,
            stacklevel=1,
        )

    def delete_metadata_properties(
        self, metadata_properties: Union[str, List[str]]
    ) -> Union["AllowedMetadataPropertyTypes", List["AllowedMetadataPropertyTypes"]]:
        """Deletes the given metadata properties from the dataset.

        Args:
            metadata_properties: the name/s of the metadata property/ies to delete.

        Returns:
            The metadata properties that were deleted.

        Raises:
            TypeError: if `metadata_properties` is not a string or a list of strings.
            ValueError: if the provided `metadata_properties` is/are not in the dataset.
        """
        if not isinstance(metadata_properties, list):
            metadata_properties = [metadata_properties]

        if not self.metadata_properties:
            raise ValueError(
                "The current `FeedbackDataset` does not contain any `metadata_properties` defined, so"
                " none can be deleted."
            )
        metadata_properties_mapping = {
            metadata_property.name: metadata_property for metadata_property in self.metadata_properties
        }
        if not all(
            metadata_property in metadata_properties_mapping.keys() for metadata_property in metadata_properties
        ):
            raise ValueError(
                f"Invalid `metadata_properties={metadata_properties}` provided. It cannot be"
                " deleted because it does not exist, make sure you delete just existing `metadata_properties`"
                " meaning that the name matches any of the existing `metadata_properties` if any. Current"
                f" `metadata_properties` are: '{', '.join(metadata_properties_mapping.keys())}'."
            )

        deleted_metadata_properties = []
        for metadata_property in metadata_properties:
            deleted_metadata_properties.append(metadata_properties_mapping.pop(metadata_property))
        self._metadata_properties = list(metadata_properties_mapping.values())
        return deleted_metadata_properties if len(deleted_metadata_properties) > 1 else deleted_metadata_properties[0]

    # TODO(alvarobartt,davidberenstein1957): we should consider having something like
    # `export(..., training=True)` to export the dataset records in any format, replacing
    # both `format_as` and `prepare_for_training`
    def prepare_for_training(
        self,
        framework: Union[Framework, str],
        task: TrainingTaskTypes,
        train_size: Optional[float] = 1,
        test_size: Optional[float] = None,
        seed: Optional[int] = None,
        lang: Optional[str] = None,
    ) -> Any:
        """
        Prepares the dataset for training for a specific training framework and NLP task by splitting the dataset into train and test sets.

        Args:
            framework: the framework to use for training. Currently supported frameworks are: `transformers`, `peft`,
                `setfit`, `spacy`, `spacy-transformers`, `span_marker`, `spark-nlp`, `openai`, `trl`, `sentence-transformers`.
            task: the NLP task to use for training. Currently supported tasks are: `TrainingTaskForTextClassification`,
                `TrainingTaskForSFT`, `TrainingTaskForRM`, `TrainingTaskForPPO`, `TrainingTaskForDPO`, `TrainingTaskForSentenceSimilarity`.
            train_size: the size of the train set. If `None`, the whole dataset will be used for training.
            test_size: the size of the test set. If `None`, the whole dataset will be used for testing.
            seed: the seed to use for splitting the dataset into train and test sets.
            lang: the spaCy language to use for training. If `None`, the language of the dataset will be used.
        """
        if isinstance(framework, str):
            framework = Framework(framework)

        # validate train and test sizes
        if train_size is None:
            train_size = 1
        if test_size is None:
            test_size = 1 - train_size

        # check if all numbers are larger than 0
        if not [abs(train_size), abs(test_size)] == [train_size, test_size]:
            raise ValueError("`train_size` and `test_size` must be larger than 0.")
        # check if train sizes sum up to 1
        if not (train_size + test_size) == 1:
            raise ValueError("`train_size` and `test_size` must sum to 1.")

        if test_size == 0:
            test_size = None

        if len(self.records) < 1:
            raise ValueError(
                "No records found in the dataset. Make sure you add records to the"
                " dataset via the `FeedbackDataset.add_records()` method first."
            )

        local_dataset = self
        if isinstance(task, (TrainingTaskForTextClassification, TrainingTaskForSentenceSimilarity)):
            if task.formatting_func is None:
                # in sentence-transformer models we can train without labels
                if task.label:
                    local_dataset = local_dataset.compute_unified_responses(
                        question=task.label.question, strategy=task.label.strategy
                    )
        elif isinstance(task, TrainingTaskForQuestionAnswering):
            if task.formatting_func is None:
                local_dataset = self.compute_unified_responses(question=task.answer.name, strategy="disagreement")
        elif not isinstance(
            task,
            (
                TrainingTaskForSFT,
                TrainingTaskForRM,
                TrainingTaskForPPO,
                TrainingTaskForDPO,
                TrainingTaskForChatCompletion,
            ),
        ):
            raise ValueError(f"Training data {type(task)} is not supported yet")

        return task.prepare_for_training(framework=framework, dataset=self, train_size=train_size, seed=seed, lang=lang)

    def update_records(self, records: Union["FeedbackRecord", List["FeedbackRecord"]]) -> None:
        warnings.warn(
            "`update_records` method only works for `FeedbackDataset` pushed to Argilla. "
            "If your are working with local data, you can just iterate over the records and update them."
        )

    def sort_by(
        self, field: Union[str, RecordSortField], order: Union[str, SortOrder] = SortOrder.asc
    ) -> "FeedbackDataset":
        warnings.warn(
            "`sort_by` method is not supported for local datasets and won't take any effect. "
            "First, you need to push the dataset to Argilla with `FeedbackDataset.push_to_argilla()`. "
            "After, use `FeedbackDataset.from_argilla(...).sort_by()`.",
            UserWarning,
            stacklevel=1,
        )
        return self

    def pull(self, *args, **kwargs) -> "FeedbackDataset":
        warnings.warn(
            "`pull` method is not supported for local datasets and won't take any effect."
            "First, you need to push the dataset to Argilla with `FeedbackDataset.push_to_argilla()`. "
            "After, use `FeedbackDataset.from_argilla(...).pull()`.",
            UserWarning,
        )
        return self

    def filter_by(self, *args, **kwargs) -> "FeedbackDataset":
        warnings.warn(
            "`filter_by` method is not supported for local datasets and won't take any effect. "
            "First, you need to push the dataset to Argilla with `FeedbackDataset.push_to_argilla()`. "
            "After, use `FeedbackDataset.from_argilla(...).filter_by()`.",
            UserWarning,
        )
        return self

    def delete(self):
        warnings.warn(
            "`delete` method is not supported for local datasets and won't take any effect. "
            "First, you need to push the dataset to Argilla with `FeedbackDataset.push_to_argilla`. "
            "After, use `FeedbackDataset.from_argilla(...).delete()`",
            UserWarning,
        )
        return self

    def find_similar_records(
        self,
        vector_name: str,
        value: Optional[List[float]] = None,
        record: Optional[R] = None,
        max_results: int = 50,
    ) -> List[Tuple[FeedbackRecord, float]]:
        warnings.warn(
            "`find_similar_records` method is not supported for local datasets and won't take any effect. "
            "First, you need to push the dataset to Argilla with `FeedbackDataset.push_to_argilla`. "
            "After, use `FeedbackDataset.from_argilla(...).find_similar_records()`",
            UserWarning,
        )
        return []
