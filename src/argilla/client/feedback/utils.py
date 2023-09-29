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

from typing import TYPE_CHECKING, List, Optional, Union

from pydantic import BaseModel, Extra, create_model

from argilla.client.api import active_client
from argilla.client.feedback.constants import FIELD_TYPE_TO_PYTHON_TYPE
from argilla.client.feedback.schemas.enums import MetadataPropertyTypes
from argilla.client.feedback.schemas.types import AllowedFieldTypes, AllowedMetadataPropertyTypes
from argilla.client.sdk.v1.datasets import api as datasets_api_v1
from argilla.client.workspaces import Workspace

if TYPE_CHECKING:
    import httpx

    from argilla.client.sdk.v1.datasets.models import FeedbackDatasetModel


def generate_pydantic_schema_for_fields(
    fields: List[AllowedFieldTypes], name: Optional[str] = "FieldsSchema"
) -> BaseModel:
    """Generates a `pydantic.BaseModel` schema from a list of `AllowedFieldTypes` objects to validate
    the fields of a `FeedbackDataset` object before inserting them.

    Args:
        fields: the list of `AllowedFieldTypes` objects to generate the schema from.
        name: the name of the `pydantic.BaseModel` schema to generate. Defaults to "FieldsSchema".

    Returns:
        A `pydantic.BaseModel` schema to validate the fields of a `FeedbackDataset` object before
        inserting them.

    Raises:
        ValueError: if one of the fields has an unsupported type.

    Examples:
        >>> from argilla.client.feedback.schemas.fields import TextField
        >>> from argilla.client.feedback.utils import generate_pydantic_schema_for_fields
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
    metadata_properties: List[AllowedMetadataPropertyTypes], name: Optional[str] = "MetadataSchema"
) -> BaseModel:
    """Generates a `pydantic.BaseModel` schema from a list of `AllowedMetadataPropertyTypes` objects to validate
    the metadata of a `FeedbackDataset` object before inserting them.

    Args:
        metadata_properties: the list of `AllowedMetadataPropertyTypes` objects to generate the schema from.
        name: the name of the `pydantic.BaseModel` schema to generate. Defaults to "MetadataSchema".

    Returns:
        A `pydantic.BaseModel` schema to validate the metadata of a `FeedbackDataset` object before
        inserting them.

    Raises:
        ValueError: if one of the metadata properties has an unsupported type.

    Examples:
        >>> from argilla.client.feedback.schemas.metadata import IntegerMetadataProperty
        >>> from argilla.client.feedback.utils import generate_pydantic_schema_for_metadata
        >>> metadata_properties = [
        ...     IntegerMetadataProperty(name="int-metadata", min=0, max=10),
        ...     ...,
        ... ]
        >>> MetadataSchema = generate_pydantic_schema_for_metadata(metadata_properties)
        >>> MetadataSchema(int-metadata=5)
        MetadataSchema(int-metadata=5)
    """
    metadata_fields, metadata_validators = {}, {}

    for metadata_property in metadata_properties:
        if metadata_property.type not in MetadataPropertyTypes:
            raise ValueError(
                f"Metadata property {metadata_property.name} has an unsupported type: {metadata_property.type}, for the moment only the"
                f" following types are supported: {[arg.value for arg in MetadataPropertyTypes]}"
            )
        pydantic_field, pydantic_validator = metadata_property._pydantic_field_with_validator
        metadata_fields.update(pydantic_field)
        metadata_validators.update(pydantic_validator)

    class MetadataConfig:
        extra = Extra.ignore

    return create_model(name, **metadata_fields, __validators__=metadata_validators, __config__=MetadataConfig)


def feedback_dataset_in_argilla(
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
        >>> from argilla.client.feedback.dataset import feedback_dataset_in_argilla
        >>> dataset = feedback_dataset_in_argilla(name="my-dataset")
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
