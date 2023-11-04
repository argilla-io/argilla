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

import typing

from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedMetadataPropertyTypes, AllowedQuestionTypes

if typing.TYPE_CHECKING:
    from argilla.client.feedback.dataset.base import FeedbackDatasetBase


def validate_fields(fields: typing.Union[AllowedFieldTypes, typing.List[AllowedFieldTypes]]):
    """Validates that the fields used in the filters are valid."""
    if not isinstance(fields, list):
        raise TypeError(f"Expected `fields` to be a list, got {type(fields)} instead.")

    any_required = False
    unique_names = set()
    for field in fields:
        if not isinstance(field, AllowedFieldTypes):
            raise TypeError(
                f"Expected `fields` to be a list of `{AllowedFieldTypes.__name__}`, got {type(field)} instead."
            )
        if field.name in unique_names:
            raise ValueError(f"Expected `fields` to have unique names, got {field.name} twice instead.")
        unique_names.add(field.name)
        if not any_required and field.required:
            any_required = True

    if not any_required:
        raise ValueError("At least one field in `fields` must be required (`required=True`).")


def validate_questions(questions: typing.Union[AllowedQuestionTypes, typing.List[AllowedQuestionTypes]]) -> None:
    """Validates that the questions used in the filters are valid."""
    if not isinstance(questions, list):
        raise TypeError(f"Expected `questions` to be a list, got {type(questions)} instead.")

    any_required = False
    unique_names = set()
    for question in questions:
        if not isinstance(question, AllowedQuestionTypes.__args__):
            raise TypeError(
                "Expected `questions` to be a list of"
                f" `{'`, `'.join([arg.__name__ for arg in AllowedQuestionTypes.__args__])}` got a"
                f" question in the list with type {type(question)} instead."
            )
        if question.name in unique_names:
            raise ValueError(f"Expected `questions` to have unique names, got {question.name} twice instead.")
        unique_names.add(question.name)
        if not any_required and question.required:
            any_required = True

    if not any_required:
        raise ValueError("At least one question in `questions` must be required (`required=True`).")


def validate_metadata_properties(metadata_properties: typing.List[AllowedMetadataPropertyTypes]) -> None:
    """Validates that the metadata properties used in the filters are valid."""

    if not metadata_properties:
        return

    unique_names = set()
    for metadata_property in metadata_properties:
        if not isinstance(metadata_property, AllowedMetadataPropertyTypes.__args__):
            raise TypeError(
                f"Expected `metadata_properties` to be a list of"
                f" `{'`, `'.join([arg.__name__ for arg in AllowedMetadataPropertyTypes.__args__])}` got a"
                f" metadata property in the list with type type {type(metadata_property)} instead."
            )
        if metadata_property.name in unique_names:
            raise ValueError(
                f"Expected `metadata_properties` to have unique names, got '{metadata_property.name}' twice instead."
            )
        unique_names.add(metadata_property.name)


def validate_metadata_names(dataset: "FeedbackDatasetBase", names: typing.List[str]) -> None:
    """Validates that the metadata names used in the filters are valid."""

    metadata_property_names = {metadata_property.name: True for metadata_property in dataset.metadata_properties}

    if not metadata_property_names:
        return

    for name in set(names):
        if not metadata_property_names.get(name):
            raise ValueError(
                f"The metadata property name `{name}` does not exist in the current `FeedbackDataset` in Argilla."
                f" The existing metadata properties names are: {list(metadata_property_names.keys())}."
            )


def validate_vector_names(dataset: "FeedbackDatasetBase", names: typing.List[str]) -> None:
    """Validates that the vector names used in the filters are valid."""
    vectors_names = {vector.name: True for vector in dataset.vectors_settings}

    if not vectors_names:
        return

    for name in set(names):
        if not vectors_names.get(name):
            raise ValueError(
                f"The vector name `{name}` does not exist in the current `FeedbackDataset` in Argilla."
                f" The existing vector names are: {list(vectors_names.keys())}."
            )
