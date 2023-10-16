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

from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Union

import pytest
from argilla.client.feedback.dataset.base import FeedbackDatasetBase
from argilla.client.feedback.schemas.enums import RecordSortField, ResponseStatusFilter, SortOrder
from argilla.client.feedback.schemas.fields import TextField
from argilla.client.feedback.schemas.metadata import (
    FloatMetadataProperty,
    IntegerMetadataProperty,
    MetadataFilters,
    TermsMetadataProperty,
)
from argilla.client.feedback.schemas.questions import RatingQuestion, TextQuestion
from argilla.client.feedback.schemas.records import FeedbackRecord

if TYPE_CHECKING:
    from argilla.client.feedback.schemas.types import (
        AllowedFieldTypes,
        AllowedMetadataPropertyTypes,
        AllowedQuestionTypes,
    )


class TestFeedbackDataset(FeedbackDatasetBase):
    def update_records(self, **kwargs: Dict[str, Any]) -> None:
        pass

    def filter_by(
        self,
        *,
        response_status: Optional[Union[ResponseStatusFilter, List[ResponseStatusFilter]]] = None,
        metadata_filters: Optional[Union[MetadataFilters, List[MetadataFilters]]] = None,
    ) -> "TestFeedbackDataset":
        return self

    def sort_by(
        self, field: Union[str, RecordSortField], order: Union[str, SortOrder] = SortOrder.asc
    ) -> "TestFeedbackDataset":
        return self

    @property
    def records(self) -> Iterable[FeedbackRecord]:
        return []


def test_init(
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
) -> None:
    dataset = TestFeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
        allow_extra_metadata=False,
    )

    assert dataset.guidelines == feedback_dataset_guidelines
    assert dataset.fields == feedback_dataset_fields
    assert dataset.questions == feedback_dataset_questions
    assert dataset.allow_extra_metadata == False


def test_init_base(
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
) -> None:
    with pytest.raises(Exception, match="Can't instantiate abstract class FeedbackDatasetBase"):
        FeedbackDatasetBase(
            guidelines=feedback_dataset_guidelines,
            fields=feedback_dataset_fields,
            questions=feedback_dataset_questions,
        )


def test_init_wrong_guidelines(
    feedback_dataset_fields: List["AllowedFieldTypes"], feedback_dataset_questions: List["AllowedQuestionTypes"]
) -> None:
    with pytest.raises(TypeError, match="Expected `guidelines` to be"):
        TestFeedbackDataset(
            guidelines=[],
            fields=feedback_dataset_fields,
            questions=feedback_dataset_questions,
        )
    with pytest.raises(ValueError, match="Expected `guidelines` to be"):
        TestFeedbackDataset(
            guidelines="",
            fields=feedback_dataset_fields,
            questions=feedback_dataset_questions,
        )


def test_init_wrong_fields(
    feedback_dataset_guidelines: str, feedback_dataset_questions: List["AllowedQuestionTypes"]
) -> None:
    with pytest.raises(TypeError, match="Expected `fields` to be a list"):
        TestFeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=None,
            questions=feedback_dataset_questions,
        )
    with pytest.raises(TypeError, match="Expected `fields` to be a list of `TextField`"):
        TestFeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=[{"wrong": "field"}],
            questions=feedback_dataset_questions,
        )
    with pytest.raises(ValueError, match="At least one field in `fields` must be required"):
        TestFeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=[TextField(name="test", required=False)],
            questions=feedback_dataset_questions,
        )
    with pytest.raises(ValueError, match="Expected `fields` to have unique names"):
        TestFeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=[
                TextField(name="test", required=True),
                TextField(name="test", required=True),
            ],
            questions=feedback_dataset_questions,
        )


def test_init_wrong_questions(
    feedback_dataset_guidelines: str, feedback_dataset_fields: List["AllowedFieldTypes"]
) -> None:
    with pytest.raises(TypeError, match="Expected `questions` to be a list, got"):
        TestFeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=feedback_dataset_fields,
            questions=None,
        )
    with pytest.raises(
        TypeError,
        match="Expected `questions` to be a list of",
    ):
        TestFeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=feedback_dataset_fields,
            questions=[{"wrong": "question"}],
        )
    with pytest.raises(ValueError, match="At least one question in `questions` must be required"):
        TestFeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=feedback_dataset_fields,
            questions=[
                TextQuestion(name="question-1", required=False),
                RatingQuestion(name="question-2", values=[1, 2], required=False),
            ],
        )
    with pytest.raises(ValueError, match="Expected `questions` to have unique names"):
        TestFeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=feedback_dataset_fields,
            questions=[
                TextQuestion(name="question-1", required=True),
                TextQuestion(name="question-1", required=True),
            ],
        )


def test_init_wrong_metadata_properties(
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
) -> None:
    with pytest.raises(TypeError, match="Expected `metadata_properties` to be a list"):
        TestFeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=feedback_dataset_fields,
            questions=feedback_dataset_questions,
            metadata_properties=["wrong type"],
        )
    with pytest.raises(ValueError, match="Expected `metadata_properties` to have unique names"):
        TestFeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=feedback_dataset_fields,
            questions=feedback_dataset_questions,
            metadata_properties=[
                IntegerMetadataProperty(name="metadata-property-1", min=0, max=10),
                IntegerMetadataProperty(name="metadata-property-1", min=0, max=10),
            ],
        )


@pytest.mark.parametrize(
    "record",
    [
        FeedbackRecord(fields={"required-field": "text"}, metadata={"nested-metadata": {"a": 1}}),
        FeedbackRecord(
            fields={"required-field": "text", "optional-field": "text"},
            metadata={"int-metadata": 1, "float-metadata": 1.0},
        ),
        FeedbackRecord(
            fields={"required-field": "text", "optional-field": None},
            metadata={"terms-metadata": "a", "more-metadata": 3},
        ),
    ],
)
def test__parse_and_validate_records_validation(record: "FeedbackRecord") -> None:
    dataset = TestFeedbackDataset(
        fields=[TextField(name="required-field", required=True), TextField(name="optional-field", required=False)],
        questions=[TextQuestion(name="question", required=True)],
        metadata_properties=[
            TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
            IntegerMetadataProperty(name="int-metadata", min=0, max=10),
            FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
        ],
    )
    dataset._parse_and_validate_records(record)


@pytest.mark.parametrize(
    "record, allow_extra_metadata, exception_cls, exception_msg",
    [
        (FeedbackRecord(fields={}, metadata={}), True, ValueError, "required-field\n  field required"),
        (
            FeedbackRecord(fields={"optional-field": "text"}, metadata={}),
            True,
            ValueError,
            "required-field\n  field required",
        ),
        (
            FeedbackRecord(fields={"required-field": "text"}, metadata={"terms-metadata": "d"}),
            True,
            ValueError,
            "terms-metadata\n  Provided 'terms-metadata=d' is not valid, only values in \['a', 'b', 'c'\] are allowed.",
        ),
        (
            FeedbackRecord(fields={"required-field": "text"}, metadata={"int-metadata": 11}),
            True,
            ValueError,
            "int-metadata\n  Provided 'int-metadata=11' is not valid, only values between 0 and 10 are allowed.",
        ),
        (
            FeedbackRecord(fields={"required-field": "text"}, metadata={"float-metadata": 11.0}),
            True,
            ValueError,
            "float-metadata\n  Provided 'float-metadata=11.0' is not valid, only values between 0.0 and 10.0 are allowed.",
        ),
        (
            FeedbackRecord(fields={"required-field": "text"}, metadata={"extra-metadata": "yes"}),
            False,
            ValueError,
            "extra fields not permitted",
        ),
    ],
)
def test__parse_and_validate_records_validation_error(
    record: FeedbackRecord,
    allow_extra_metadata: bool,
    exception_cls: Exception,
    exception_msg: str,
) -> None:
    dataset = TestFeedbackDataset(
        fields=[TextField(name="required-field", required=True), TextField(name="optional-field", required=False)],
        questions=[TextQuestion(name="question", required=True)],
        metadata_properties=[
            TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
            IntegerMetadataProperty(name="int-metadata", min=0, max=10),
            FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
        ],
        allow_extra_metadata=allow_extra_metadata,
    )
    with pytest.raises(exception_cls, match=exception_msg):
        dataset._parse_and_validate_records(record)


@pytest.mark.parametrize(
    "metadata_property",
    (
        TermsMetadataProperty(name="terms-metadata-diff-name", values=["a", "b", "c"]),
        IntegerMetadataProperty(name="int-metadata-diff-name", min=0, max=10),
        FloatMetadataProperty(name="float-metadata-diff-name", min=0.0, max=10.0),
    ),
)
def test__unique_metadata_property(metadata_property: "AllowedMetadataPropertyTypes") -> None:
    dataset = TestFeedbackDataset(
        fields=[TextField(name="required-field", required=True), TextField(name="optional-field", required=False)],
        questions=[TextQuestion(name="question", required=True)],
        metadata_properties=[
            TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
            IntegerMetadataProperty(name="int-metadata", min=0, max=10),
            FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
        ],
    )
    dataset._unique_metadata_property(metadata_property)
