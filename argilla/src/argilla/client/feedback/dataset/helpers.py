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
from typing import Any, Dict, List, Optional, Type, Union

import httpx

from argilla.client.feedback.constants import FIELD_TYPE_TO_PYTHON_TYPE
from argilla.client.feedback.dataset.base import FeedbackDatasetBase
from argilla.client.feedback.schemas import FeedbackRecord
from argilla.client.feedback.schemas.enums import MetadataPropertyTypes
from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedMetadataPropertyTypes, AllowedQuestionTypes
from argilla.client.sdk.v1.datasets import api as datasets_api_v1
from argilla.client.sdk.v1.datasets.models import FeedbackDatasetModel
from argilla.client.singleton import active_client
from argilla.client.workspaces import Workspace
from argilla.pydantic_v1 import BaseModel, Extra, ValidationError, create_model

if typing.TYPE_CHECKING:
    from argilla.client.feedback.schemas.types import (
        AllowedFieldTypes,
        AllowedMetadataPropertyTypes,
        AllowedRemoteFieldTypes,
        AllowedRemoteMetadataPropertyTypes,
    )


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


def validate_metadata_properties(
    metadata_properties: typing.Union[typing.List[AllowedMetadataPropertyTypes], None]
) -> None:
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


def normalize_records(
    records: Union[FeedbackRecord, Dict[str, Any], List[Union[FeedbackRecord, Dict[str, Any]]]]
) -> List[FeedbackRecord]:
    """Parses the records into a list of `FeedbackRecord` objects.

    Args:
        records: either a single `FeedbackRecord` or `dict` or a list of `FeedbackRecord` or `dict`.

    Returns:
        A list of `FeedbackRecord` objects.

    Raises:
        ValueError: if `records` is not a `FeedbackRecord` or `dict` or a list of `FeedbackRecord` or `dict`.
    """
    if isinstance(records, (dict, FeedbackRecord)):
        records = [records]

    if len(records) == 0:
        raise ValueError("Expected `records` to be a non-empty list of `dict` or `FeedbackRecord`.")

    new_records = []
    for record in records:
        if isinstance(record, dict):
            new_records.append(FeedbackRecord(**record))
        elif isinstance(record, FeedbackRecord):
            new_records.append(record)
        else:
            raise ValueError(
                "Expected `records` to be a list of `dict` or `FeedbackRecord`," f" got type `{type(record)}` instead."
            )
    return new_records


def validate_dataset_records(
    dataset: FeedbackDatasetBase,
    records: List[FeedbackRecord],
    attributes_to_validate: typing.Optional[List[str]] = None,
) -> None:
    """Validates the records against the schema defined by the `fields`.

    Args:
        dataset: the `FeedbackDataset` object to validate the records against.
        records: a list of `FeedbackRecord` objects to validate.
        attributes_to_validate: a list containing the name of the attributes to
            validate from the record. Valid values are: `fields`, `metadata` and `vectors`.
            If not provided, all `fields`, `metadata` and `vectors` are validated. Defaults
            to `None`.

    Raises:
        ValueError: if the `fields` schema does not match the `FeedbackRecord.fields` schema.
    """
    attributes_to_validate = attributes_to_validate or ["fields", "metadata", "vectors"]

    if "fields" in attributes_to_validate:
        fields_schema = _build_fields_schema(dataset)

    if "metadata" in attributes_to_validate:
        metadata_schema = _build_metadata_schema(dataset)

    if "vectors" in attributes_to_validate:
        vectors_settings_by_name = {
            vector_settings.name: vector_settings for vector_settings in dataset.vectors_settings or []
        }

    for record in records:
        if "fields" in attributes_to_validate:
            _validate_record_fields(record, fields_schema)

        if "metadata" in attributes_to_validate:
            _validate_record_metadata(record, metadata_schema)

        if "vectors" in attributes_to_validate:
            _validate_record_vectors(record, vectors_settings_by_name)


def get_dataset_by_name_and_workspace(
    name: Optional[str] = None, *, workspace: Optional[Union[str, Workspace]] = None, id: Optional[str] = None
) -> Optional["FeedbackDatasetModel"]:
    """Checks whether a `FeedbackDataset` exists in Argilla or not, based on the `name`, `id`, or the combination of
    `name` and `workspace`.

    Args:
        name: the name of the `FeedbackDataset` in Argilla.
        workspace: the name of the workspace in Argilla where the `FeedbackDataset` is located.
        id: the Argilla ID of the `FeedbackDataset`.

    Returns:
        The `FeedbackDataset` if it exists in Argilla, `None` otherwise.

    Raises:
        ValueError: if the `workspace` is not a `Workspace` instance or a string.
        Exception: if the `FeedbackDataset` could not be listed from Argilla.

    Examples:
        >>> import argilla as rg
        >>> rg.init(api_url="...", api_key="...")
        >>> from argilla.client.feedback.dataset.helpers import get_dataset_by_name_and_workspace
        >>> dataset = get_dataset_by_name_and_workspace(name="my-dataset")
    """
    assert (name and workspace) or name or id, (
        "You must provide either the `name` and `workspace` (the latter just if"
        " applicable, if not the default `workspace` will be used) or the `id`, which"
        " is the Argilla ID of the `rg.FeedbackDataset`."
    )

    client = active_client()
    httpx_client: "httpx.Client" = client.http_client.httpx

    if name:
        if workspace is None:
            workspace = Workspace.from_name(client.get_workspace())
        elif isinstance(workspace, str):
            workspace = Workspace.from_name(workspace)
        elif not isinstance(workspace, Workspace):
            raise ValueError(f"Workspace must be a `rg.Workspace` instance or a string, got {type(workspace)}")

        try:
            datasets = datasets_api_v1.list_datasets(client=httpx_client).parsed
        except Exception as e:
            raise Exception(f"Failed while listing the `FeedbackTask` datasets from Argilla with exception: {e}")

        for dataset in datasets:
            if dataset.name == name and dataset.workspace_id == workspace.id:
                return dataset
        return None
    elif id:
        try:
            return datasets_api_v1.get_dataset(client=httpx_client, id=id).parsed
        except Exception:
            return None
    else:
        raise ValueError("You must provide either the `name` and `workspace` or the `id` of the `FeedbackDataset`.")


def generate_pydantic_schema_for_fields(
    fields: List[Union["AllowedFieldTypes", "AllowedRemoteFieldTypes"]], name: Optional[str] = "FieldsSchema"
) -> typing.Type[BaseModel]:
    """Generates a `pydantic.BaseModel` schema from a list of `AllowedFieldTypes` or `AllowedRemoteFieldTypes`
    objects to validate the fields of a `FeedbackDataset` or `RemoteFeedbackDataset` object, respectively,
    before inserting them.

    Args:
        fields: the list of `AllowedFieldTypes` or `AllowedRemoteFieldTypes` objects to generate the schema from.
        name: the name of the `pydantic.BaseModel` schema to generate. Defaults to "FieldsSchema".

    Returns:
        A `pydantic.BaseModel` schema to validate the fields of a `FeedbackDataset` or `RemoteFeedbackDataset`
        object before inserting them.

    Raises:
        ValueError: if one of the fields has an unsupported type.

    Examples:
        >>> from argilla.client.feedback.schemas.fields import TextField
        >>> from argilla.client.feedback.dataset.helpers import generate_pydantic_schema_for_fields
        >>> fields = [
        ...     TextField(name="text", required=True),
        ...     TextField(name="label", required=True),
        ... ]
        >>> FieldsSchema = generate_pydantic_schema_for_fields(fields)
        >>> FieldsSchema(text="Hello", label="World")
        FieldsSchema(text='Hello', label='World')
    """
    fields_schema = {}
    for field in fields:
        if field.type not in FIELD_TYPE_TO_PYTHON_TYPE.keys():
            raise ValueError(
                f"Field {field.name} has an unsupported type: {field.type}, for the moment only the"
                f" following types are supported: {list(FIELD_TYPE_TO_PYTHON_TYPE.keys())}"
            )
        fields_schema.update({field.name: (FIELD_TYPE_TO_PYTHON_TYPE[field.type], ... if field.required else None)})
    return create_model(name, **fields_schema)


def generate_pydantic_schema_for_metadata(
    metadata_properties: List[Union["AllowedMetadataPropertyTypes", "AllowedRemoteMetadataPropertyTypes"]],
    name: Optional[str] = "MetadataSchema",
    allow_extra_metadata: bool = True,
) -> Type[BaseModel]:
    """Generates a `pydantic.BaseModel` schema from a list of `AllowedMetadataPropertyTypes` or
    `AllowedRemoteMetadataPropertyTypes` objects to validate the metadata of a `FeedbackDataset`
    or `RemoteFeedbackDataset` object, respectively, before inserting them.

    Args:
        metadata_properties: the list of `AllowedMetadataPropertyTypes` or `AllowedRemoteMetadataPropertyTypes`
            objects to generate the schema from.
        name: the name of the `pydantic.BaseModel` schema to generate. Defaults to "MetadataSchema".
        allow_extra_metadata: whether to allow extra metadata properties or not. Defaults to `True`.

    Returns:
        A `pydantic.BaseModel` schema to validate the metadata of a `FeedbackDataset` or `RemoteFeedbackDataset`
        object before inserting them.

    Raises:
        ValueError: if one of the metadata properties has an unsupported type.

    Examples:
        >>> from argilla.client.feedback.schemas.metadata import IntegerMetadataProperty
        >>> from argilla.client.feedback.dataset.helpers import generate_pydantic_schema_for_metadata
        >>> metadata_properties = [
        ...     IntegerMetadataProperty(name="int_metadata", min=0, max=10),
        ...     ...,
        ... ]
        >>> MetadataSchema = generate_pydantic_schema_for_metadata(metadata_properties)
        >>> MetadataSchema(int_metadata=5)
        MetadataSchema(int-metadata=5)
    """
    metadata_fields, metadata_validators = {}, {}

    for metadata_property in metadata_properties or []:
        if metadata_property.type not in [arg.value for arg in MetadataPropertyTypes]:
            raise ValueError(
                f"Metadata property {metadata_property.name} has an unsupported type: {metadata_property.type}, for the moment only the"
                f" following types are supported: {[arg.value for arg in MetadataPropertyTypes]}"
            )
        pydantic_field, pydantic_validator = metadata_property._pydantic_field_with_validator
        metadata_fields.update(pydantic_field)
        metadata_validators.update(pydantic_validator)

    class MetadataConfig:
        extra = Extra.allow if allow_extra_metadata else Extra.forbid

    return create_model(name, **metadata_fields, __validators__=metadata_validators, __config__=MetadataConfig)


def _validate_record_fields(record: FeedbackRecord, fields_schema: typing.Type[BaseModel]) -> None:
    """Validates the `FeedbackRecord.fields` against the schema defined by the `fields`."""
    try:
        fields_schema.parse_obj(record.fields)
    except ValidationError as e:
        raise ValueError(f"`FeedbackRecord.fields` does not match the expected schema, with exception: {e}") from e


def _validate_record_metadata(record: FeedbackRecord, metadata_schema: typing.Type[BaseModel] = None) -> None:
    """Validates the `FeedbackRecord.metadata` against the schema defined by the `metadata_properties`."""

    if not record.metadata:
        return

    try:
        metadata_schema.parse_obj(record.metadata)
    except ValidationError as e:
        raise ValueError(
            f"`FeedbackRecord.metadata` {record.metadata} does not match the expected schema," f" with exception: {e}"
        ) from e


def _validate_record_vectors(record: FeedbackRecord, vectors_settings_by_name) -> None:
    for vector_name, vector_value in record.vectors.items():
        if not vectors_settings_by_name.get(vector_name):
            raise ValueError(f"Vector with name `{vector_name}` not present on dataset vector settings.")

        if vectors_settings_by_name[vector_name].dimensions != (record_vector_dimension := len(vector_value)):
            raise ValueError(
                f"Vector with name `{vector_name}` has an invalid expected dimension. {record_vector_dimension}"
            )

        if not (isinstance(vector_value, list) and all(isinstance(v, float) for v in vector_value)):
            raise ValueError(
                f"Vector with name `{vector_name}` has an invalid type. "
                f"Expected `list[float]`, got `{type(vector_value)}`."
            )


def _build_fields_schema(dataset: FeedbackDatasetBase) -> Type[BaseModel]:
    """Returns the fields schema of the dataset."""
    return generate_pydantic_schema_for_fields(dataset.fields)


def _build_metadata_schema(dataset: FeedbackDatasetBase) -> Type[BaseModel]:
    """Returns the metadata schema of the dataset."""
    return generate_pydantic_schema_for_metadata(
        dataset.metadata_properties, allow_extra_metadata=dataset.allow_extra_metadata
    )
