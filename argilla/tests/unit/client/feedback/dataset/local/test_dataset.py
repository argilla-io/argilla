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

from typing import TYPE_CHECKING, List, Type

import numpy.array_api
import pytest
from argilla_v1 import RatingQuestion
from argilla_v1.client.feedback.dataset.local.dataset import FeedbackDataset
from argilla_v1.client.feedback.schemas.fields import TextField
from argilla_v1.client.feedback.schemas.metadata import (
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
)
from argilla_v1.client.feedback.schemas.questions import TextQuestion
from argilla_v1.client.feedback.schemas.records import FeedbackRecord
from argilla_v1.client.feedback.schemas.vector_settings import VectorSettings

if TYPE_CHECKING:
    from argilla_v1.client.feedback.schemas.types import (
        AllowedFieldTypes,
        AllowedMetadataPropertyTypes,
        AllowedQuestionTypes,
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
        FeedbackRecord(
            fields={"required-field": "text", "optional-field": None},
            vectors={"vector-1": [1.0, 2.0, 3.0], "vector-2": [1.0, 2.0, 3.0, 4.0]},
        ),
    ],
)
def test_add_records_validation(record: "FeedbackRecord") -> None:
    dataset = FeedbackDataset(
        fields=[TextField(name="required-field", required=True), TextField(name="optional-field", required=False)],
        questions=[TextQuestion(name="question", required=True)],
        metadata_properties=[
            TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
            IntegerMetadataProperty(name="int-metadata", min=0, max=10),
            FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
        ],
        vectors_settings=[
            VectorSettings(name="vector-1", dimensions=3),
            VectorSettings(name="vector-2", dimensions=4),
        ],
    )

    dataset.add_records(record)
    assert len(dataset.records) == 1
    assert dataset.records[0] == record


def test_update_records_with_warning() -> None:
    dataset = FeedbackDataset(
        fields=[TextField(name="required-field")],
        questions=[TextQuestion(name="question")],
    )

    with pytest.warns(
        UserWarning,
        match="`update_records` method only works for `FeedbackDataset` pushed to Argilla."
        " If your are working with local data, you can just iterate over the records and update them.",
    ):
        dataset.update_records(
            FeedbackRecord(fields={"required-field": "text"}, metadata={"nested-metadata": {"a": 1}})
        )


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
        (
            FeedbackRecord(
                fields={"required-field": "text"},
                vectors={
                    "vector-1": [1.0, 2.0, 3.0, 4.0],
                    "vector-2": [1.0, 2.0, 3.0, 4.0],
                },
            ),
            False,
            ValueError,
            "Vector with name `vector-1` has an invalid expected dimension.",
        ),
        (
            FeedbackRecord(
                fields={"required-field": "text"},
                vectors={"vector-1": [1.0, 2.0, 3.0], "vector-2": [1.0, 2.0, 3.0, 4.0, 5.0]},
            ),
            False,
            ValueError,
            "Vector with name `vector-2` has an invalid expected dimension.",
        ),
        (
            FeedbackRecord(
                fields={"required-field": "text"},
                vectors={
                    "vector-1": [1.0, 2.0, 3.0],
                    "vector-2": [1.0, 2.0, 3.0, 4.0],
                    "vector-3": [1.0, 2.0, 3.0],
                },
            ),
            False,
            ValueError,
            "Vector with name `vector-3` not present on dataset vector settings.",
        ),
    ],
)
def test_add_records_validation_error(
    record: FeedbackRecord, allow_extra_metadata: bool, exception_cls: Exception, exception_msg: str
) -> None:
    dataset = FeedbackDataset(
        fields=[TextField(name="required-field", required=True), TextField(name="optional-field", required=False)],
        questions=[TextQuestion(name="question", required=True)],
        metadata_properties=[
            TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
            IntegerMetadataProperty(name="int-metadata", min=0, max=10),
            FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
        ],
        vectors_settings=[
            VectorSettings(name="vector-1", dimensions=3),
            VectorSettings(name="vector-2", dimensions=4),
        ],
        allow_extra_metadata=allow_extra_metadata,
    )

    with pytest.raises(exception_cls, match=exception_msg):
        dataset.add_records(record)
    assert len(dataset.records) == 0


@pytest.mark.parametrize(
    "metadata_property",
    (
        TermsMetadataProperty(name="new-terms-metadata"),
        TermsMetadataProperty(name="new-terms-metadata", values=["a", "b", "c"]),
        IntegerMetadataProperty(name="new-integer-metadata"),
        IntegerMetadataProperty(name="new-integer-metadata", min=0, max=10),
        FloatMetadataProperty(name="new-float-metadata"),
        FloatMetadataProperty(name="new-float-metadata", min=0, max=10),
    ),
)
def test_add_metadata_property(metadata_property: "AllowedMetadataPropertyTypes") -> None:
    dataset = FeedbackDataset(
        fields=[
            TextField(name="required-field"),
            TextField(name="optional-field", required=False),
        ],
        questions=[TextQuestion(name="question")],
    )

    new_metadata_property = dataset.add_metadata_property(metadata_property)
    assert new_metadata_property.name == metadata_property.name
    assert len(dataset.metadata_properties) == 1

    current_number_of_metadata_properties = len(dataset.metadata_properties)
    dataset.add_metadata_property(TermsMetadataProperty(name="new-metadata-property", values=["a", "b", "c"]))
    assert len(dataset.metadata_properties) == current_number_of_metadata_properties + 1


@pytest.mark.parametrize("property_class", [IntegerMetadataProperty, FloatMetadataProperty])
@pytest.mark.parametrize("numpy_type", [numpy.int16, numpy.int32, numpy.int64, numpy.float16, numpy.float32])
def test_add_record_with_numpy_values(property_class: Type["AllowedMetadataPropertyTypes"], numpy_type: Type) -> None:
    dataset = FeedbackDataset(
        fields=[
            TextField(name="required-field"),
            TextField(name="optional-field", required=False),
        ],
        questions=[TextQuestion(name="question")],
    )

    metadata_property = property_class(name="numeric_property")
    dataset.add_metadata_property(metadata_property)

    property_to_expected_type_msg = {IntegerMetadataProperty: "`int`", FloatMetadataProperty: "`int` or `float`"}
    expected_type_msg = property_to_expected_type_msg[property_class]

    value = numpy_type(10.0)
    record = FeedbackRecord(fields={"required-field": "text"}, metadata={"numeric_property": value})

    with pytest.raises(
        ValueError,
        match=f"Provided 'numeric_property={value}' of type {str(numpy_type)} is not valid, "
        f"only values of type {expected_type_msg} are allowed.",
    ):
        dataset.add_records(record)


@pytest.mark.parametrize(
    "metadata_property",
    (
        TermsMetadataProperty(name="terms-metadata"),
        TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
        IntegerMetadataProperty(name="int-metadata"),
        IntegerMetadataProperty(name="int-metadata", min=0, max=10),
        FloatMetadataProperty(name="float-metadata"),
        FloatMetadataProperty(name="float-metadata", min=0, max=10),
    ),
)
def test_add_metadata_property_errors(metadata_property: "AllowedMetadataPropertyTypes") -> None:
    dataset = FeedbackDataset(
        fields=[TextField(name="required-field", required=True), TextField(name="optional-field", required=False)],
        questions=[TextQuestion(name="question", required=True)],
        metadata_properties=[
            TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
            IntegerMetadataProperty(name="int-metadata", min=0, max=10),
            FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
        ],
    )

    with pytest.raises(
        ValueError, match=f"Invalid `metadata_property={metadata_property.name}` provided as it already exists"
    ):
        _ = dataset.add_metadata_property(metadata_property)
    assert len(dataset.metadata_properties) == 3


def test_update_metadata_properties() -> None:
    dataset = FeedbackDataset(
        fields=[TextField(name="required-field", required=True), TextField(name="optional-field", required=False)],
        questions=[TextQuestion(name="question", required=True)],
        metadata_properties=[
            TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
            IntegerMetadataProperty(name="int-metadata", min=0, max=10),
            FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
        ],
    )
    for metadata_property in dataset.metadata_properties:
        metadata_property.title = "new-title"
        metadata_property.visible_for_annotators = False

    with pytest.warns(
        UserWarning, match="`update_metadata_properties` method is not supported for `FeedbackDataset` datasets"
    ):
        dataset.update_metadata_properties(dataset.metadata_properties[0])

    with pytest.warns(
        UserWarning, match="`update_metadata_properties` method is not supported for `FeedbackDataset` datasets"
    ):
        dataset.update_metadata_properties(dataset.metadata_properties)


@pytest.mark.parametrize(
    "metadata_properties",
    (
        [TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"])],
        [IntegerMetadataProperty(name="integer-metadata", min=0, max=10)],
        [FloatMetadataProperty(name="float-metadata", min=0, max=10)],
        [
            TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
            IntegerMetadataProperty(name="integer-metadata", min=0, max=10),
            FloatMetadataProperty(name="float-metadata", min=0, max=10),
        ],
    ),
)
def test_delete_metadata_properties(metadata_properties: List["AllowedMetadataPropertyTypes"]) -> None:
    dataset = FeedbackDataset(
        fields=[TextField(name="required-field", required=True), TextField(name="optional-field", required=False)],
        questions=[TextQuestion(name="question", required=True)],
        metadata_properties=metadata_properties,
    )

    deleted_metadata_properties = dataset.delete_metadata_properties(
        [metadata_property.name for metadata_property in metadata_properties]
    )
    assert len(dataset.metadata_properties) == 0
    deleted_metadata_properties = (
        deleted_metadata_properties if isinstance(deleted_metadata_properties, list) else [deleted_metadata_properties]
    )
    assert all(
        metadata_property.name
        in [deleted_metadata_property.name for deleted_metadata_property in deleted_metadata_properties]
        for metadata_property in metadata_properties
    )


def test_delete_metadata_properties_errors() -> None:
    dataset = FeedbackDataset(
        fields=[TextField(name="required-field", required=True), TextField(name="optional-field", required=False)],
        questions=[TextQuestion(name="question", required=True)],
        metadata_properties=[
            TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
            IntegerMetadataProperty(name="int-metadata", min=0, max=10),
            FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
        ],
    )

    with pytest.raises(
        ValueError,
        match="Invalid `metadata_properties=\['invalid-metadata'\]` provided. It cannot be deleted because it does not exist",
    ):
        _ = dataset.delete_metadata_properties(["invalid-metadata"])
    assert len(dataset.metadata_properties) == 3


def test_delete_vectors_settings() -> None:
    dataset = FeedbackDataset(
        fields=[TextField(name="field", required=True)],
        questions=[TextQuestion(name="question", required=True)],
        vectors_settings=[
            VectorSettings(name="vector-settings-1", dimensions=10),
            VectorSettings(name="vector-settings-2", dimensions=10),
            VectorSettings(name="vector-settings-3", dimensions=10),
        ],
    )

    deleted_vectors_settings = dataset.delete_vectors_settings("vector-settings-1")
    assert isinstance(deleted_vectors_settings, VectorSettings)
    assert len(dataset.vectors_settings) == 2

    deleted_vectors_settings = dataset.delete_vectors_settings(["vector-settings-2", "vector-settings-3"])
    assert isinstance(deleted_vectors_settings, list)
    assert len(deleted_vectors_settings) == 2
    assert len(dataset.vectors_settings) == 0


def test_not_implemented_methods():
    dataset = FeedbackDataset(
        fields=[TextField(name="required-field", required=True), TextField(name="optional-field", required=False)],
        questions=[TextQuestion(name="question", required=True)],
        metadata_properties=[
            TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
            IntegerMetadataProperty(name="int-metadata", min=0, max=10),
            FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
        ],
    )

    with pytest.warns(
        UserWarning, match="`sort_by` method is not supported for local datasets and won't take any effect. "
    ):
        assert dataset.sort_by("field") == dataset

    with pytest.warns(
        UserWarning, match="`filter_by` method is not supported for local datasets and won't take any effect. "
    ):
        assert dataset.filter_by() == dataset


def test_init(
    feedback_dataset_guidelines: str,
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
) -> None:
    dataset = FeedbackDataset(
        guidelines=feedback_dataset_guidelines,
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
        allow_extra_metadata=False,
    )

    assert dataset.guidelines == feedback_dataset_guidelines
    assert dataset.fields == feedback_dataset_fields
    assert dataset.questions == feedback_dataset_questions
    assert dataset.allow_extra_metadata == False


def test_init_wrong_guidelines(
    feedback_dataset_fields: List["AllowedFieldTypes"], feedback_dataset_questions: List["AllowedQuestionTypes"]
) -> None:
    with pytest.raises(TypeError, match="Expected `guidelines` to be"):
        FeedbackDataset(
            guidelines=[],
            fields=feedback_dataset_fields,
            questions=feedback_dataset_questions,
        )
    with pytest.raises(ValueError, match="Expected `guidelines` to be"):
        FeedbackDataset(
            guidelines="",
            fields=feedback_dataset_fields,
            questions=feedback_dataset_questions,
        )


def test_init_wrong_fields(
    feedback_dataset_guidelines: str, feedback_dataset_questions: List["AllowedQuestionTypes"]
) -> None:
    with pytest.raises(TypeError, match="Expected `fields` to be a list"):
        FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=None,
            questions=feedback_dataset_questions,
        )
    with pytest.raises(TypeError, match="Expected `fields` to be a list of `TextField`"):
        FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=[{"wrong": "field"}],
            questions=feedback_dataset_questions,
        )
    with pytest.raises(ValueError, match="At least one field in `fields` must be required"):
        FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=[TextField(name="test", required=False)],
            questions=feedback_dataset_questions,
        )
    with pytest.raises(ValueError, match="Expected `fields` to have unique names"):
        FeedbackDataset(
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
        FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=feedback_dataset_fields,
            questions=None,
        )
    with pytest.raises(
        TypeError,
        match="Expected `questions` to be a list of",
    ):
        FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=feedback_dataset_fields,
            questions=[{"wrong": "question"}],
        )
    with pytest.raises(ValueError, match="At least one question in `questions` must be required"):
        FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=feedback_dataset_fields,
            questions=[
                TextQuestion(name="question-1", required=False),
                RatingQuestion(name="question-2", values=[1, 2], required=False),
            ],
        )
    with pytest.raises(ValueError, match="Expected `questions` to have unique names"):
        FeedbackDataset(
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
        FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=feedback_dataset_fields,
            questions=feedback_dataset_questions,
            metadata_properties=["wrong type"],
        )
    with pytest.raises(ValueError, match="Expected `metadata_properties` to have unique names"):
        FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=feedback_dataset_fields,
            questions=feedback_dataset_questions,
            metadata_properties=[
                IntegerMetadataProperty(name="metadata-property-1", min=0, max=10),
                IntegerMetadataProperty(name="metadata-property-1", min=0, max=10),
            ],
        )


@pytest.mark.parametrize(
    "metadata_property",
    (
        TermsMetadataProperty(name="terms-metadata-diff-name", values=["a", "b", "c"]),
        IntegerMetadataProperty(name="int-metadata-diff-name", min=0, max=10),
        FloatMetadataProperty(name="float-metadata-diff-name", min=0.0, max=10.0),
    ),
)
def test__unique_metadata_property(metadata_property: "AllowedMetadataPropertyTypes") -> None:
    dataset = FeedbackDataset(
        fields=[TextField(name="required-field", required=True), TextField(name="optional-field", required=False)],
        questions=[TextQuestion(name="question", required=True)],
        metadata_properties=[
            TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
            IntegerMetadataProperty(name="int-metadata", min=0, max=10),
            FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
        ],
    )
    dataset._unique_metadata_property(metadata_property)


def test_properties_by_name() -> None:
    dataset = FeedbackDataset(
        fields=[TextField(name="required-field", required=True), TextField(name="optional-field", required=False)],
        questions=[TextQuestion(name="question", required=True)],
        metadata_properties=[TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"])],
    )
    assert dataset.field_by_name("mock") is None
    assert dataset.question_by_name("mock") is None
    assert dataset.metadata_property_by_name("mock") is None
    assert isinstance(dataset.field_by_name("required-field"), TextField)
    assert isinstance(dataset.question_by_name("question"), TextQuestion)
    assert isinstance(dataset.metadata_property_by_name("terms-metadata"), TermsMetadataProperty)
