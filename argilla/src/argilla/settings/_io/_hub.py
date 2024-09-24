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

import httpx
import warnings
from enum import Enum
from typing import Any, Dict, TYPE_CHECKING, Union, List, Optional

from argilla._exceptions._hub import DatasetsServerException
from argilla._exceptions._settings import SettingsError

if TYPE_CHECKING:
    from argilla import Settings

DATASETS_SERVER_BASE_URL = "https://datasets-server.huggingface.co"
DATASETS_SERVER_HEADERS = {"Accept": "application/json"}
DATASETS_SERVER_TIMEOUT = 30


class FeatureType(Enum):
    TEXT = "text"
    CHAT = "chat"
    IMAGE = "image"
    LABEL = "label"
    INT = "int"
    FLOAT = "float"


class AttributeType(Enum):
    QUESTION = "question"
    FIELD = "field"
    METADATA = "metadata"


def _get_dataset_features(repo_id: str) -> Dict[str, Dict[str, Any]]:
    """Get the features of a dataset from the datasets server using the repo_id and config.
    Extract the features from the response and return them as a dictionary.

    Parameters:
        repo_id (str): The repository ID of the dataset.

    Returns:
        Dict[str, Dict[str, Any]]: The features of the dataset.
    """

    url = f"{DATASETS_SERVER_BASE_URL}/info?dataset={repo_id}"

    try:
        with httpx.Client(
            base_url=DATASETS_SERVER_BASE_URL, headers=DATASETS_SERVER_HEADERS, timeout=DATASETS_SERVER_TIMEOUT
        ) as client:
            response = client.get(url, headers=DATASETS_SERVER_HEADERS)
            response.raise_for_status()
            response_json = response.json()

            dataset_info = response_json["dataset_info"]
            available_configs = list(dataset_info.keys())

            if len(available_configs) > 1:
                warnings.warn("Multiple configurations found. Using the first one.")
            config = available_configs[0]
            features = dataset_info[config]["features"]
            return features

    except (httpx.RequestError, httpx.HTTPStatusError, KeyError) as e:
        raise DatasetsServerException(f"Failed to get dataset info from the datasets server. Error: {str(e)}") from e


def _map_feature_type(feature):
    """Map the feature type to the corresponding FeatureType enum."""

    if isinstance(feature, list) and len(feature) > 0 and isinstance(feature[0], dict):
        sub_feature = feature[0]
        if _is_chat_feature(sub_feature):
            return FeatureType.CHAT
    elif not isinstance(feature, dict):
        warnings.warn(f"Unsupported feature format: {feature}")
        return None

    hf_type = feature.get("_type")
    dtype = feature.get("dtype")

    if hf_type == "Value":
        if dtype == "string":
            return FeatureType.TEXT
        elif dtype in ["int32", "int64"]:
            return FeatureType.INT
        elif dtype in ["float32", "float64"]:
            return FeatureType.FLOAT
    elif hf_type == "Image":
        return FeatureType.IMAGE
    elif hf_type == "ClassLabel":
        return FeatureType.LABEL
    else:
        warnings.warn(f"Unsupported feature type. hf_type: {hf_type}, dtype: {dtype}")


def _map_attribute_type(attribute_type):
    """Map the attribute type to the corresponding AttributeType enum."""
    if attribute_type == "question":
        return AttributeType.QUESTION
    elif attribute_type == "field":
        return AttributeType.FIELD
    elif attribute_type == "metadata":
        return AttributeType.METADATA
    else:
        warnings.warn(f"Unsupported attribute type: {attribute_type}")


def _is_chat_feature(sub_features):
    """Check if the sub_features correspond to an rg.ChatField."""
    return (
        "content" in sub_features
        and "role" in sub_features
        and sub_features["content"]["_type"] == "Value"
        and sub_features["role"]["_type"] == "Value"
        and sub_features["content"].get("dtype") == "string"
        and sub_features["role"].get("dtype") == "string"
    )


def _render_code_snippet(repo_id: str):
    """Render the code snippet to use feature_mapping load a dataset and log its records."""
    from rich.console import Console
    from rich.syntax import Syntax

    message = """
    You can assign the dataset's columns to questions, fields, or metadata properties using the feature_mapping argument.
    You can also add custom settings to the dataset by manipulting the settings object.
    """
    code_block = f"""
    settings = rg.Settings(
        repo_id="{repo_id}",
        feature_mapping={{{{"<column_name>": "question"}}}}
    )
    # add more custom settings here
    # via settings.questions, settings.fields, settings.vectors, or settings.metadata
    dataset = rg.Dataset(name="{repo_id}", settings=settings)
    ds = load_dataset("{repo_id}")
    dataset.records.log(ds)
    """

    console = Console()
    code_block = Syntax(code_block, "python", theme="monokai", line_numbers=True)
    console.print(f"[bold yellow]{message}[/bold yellow]")
    console.print(code_block)


def _define_settings_from_features(
    features: Union[List[Dict], Dict[str, Any]], feature_mapping: Optional[Dict[str, str]], repo_id: str
) -> "Settings":
    """Define the argilla settings from the features of a dataset.

    Parameters:
        features (Dict[str, Dict[str, Any]): The features of the dataset.

    Returns:
        rg.Settings: The settings defined from the features.
    """

    from argilla import (
        ImageField,
        LabelQuestion,
        TextQuestion,
        Settings,
        TextField,
        ChatField,
        TermsMetadataProperty,
        IntegerMetadataProperty,
        FloatMetadataProperty,
    )

    fields = []
    questions = []
    metadata = []
    feature_mapping = feature_mapping or {}

    for name, feature in features.items():
        feature_type = _map_feature_type(feature)
        attribute_definition = _map_attribute_type(feature_mapping.get(name))

        if feature_type == FeatureType.CHAT:
            fields.append(ChatField(name=name, required=False))
        elif feature_type == FeatureType.TEXT:
            if attribute_definition == AttributeType.QUESTION:
                questions.append(TextQuestion(name=name, required=False))
            elif attribute_definition == AttributeType.FIELD:
                fields.append(TextField(name=name, required=False))
            elif attribute_definition is None:
                fields.append(TextField(name=name, required=False))
            else:
                raise SettingsError(
                    f"Attribute definition '{attribute_definition}' is not supported for feature '{name}'."
                )

        elif feature_type == FeatureType.IMAGE:
            fields.append(ImageField(name=name, required=False))

        elif feature_type == FeatureType.LABEL:
            names = feature.get("names")
            if names is None:
                warnings.warn(f"Feature '{name}' has no labels. Skipping.")
                continue
            if attribute_definition == AttributeType.QUESTION or attribute_definition is None:
                questions.append(LabelQuestion(name=name, labels=names, required=False))
            elif attribute_definition == AttributeType.FIELD:
                metadata.append(TermsMetadataProperty(name=name))
            else:
                raise SettingsError(
                    f"Attribute definition '{attribute_definition}' is not supported for feature '{name}'."
                )
        elif feature_type == FeatureType.INT:
            metadata.append(IntegerMetadataProperty(name=name))
        elif feature_type == FeatureType.FLOAT:
            metadata.append(FloatMetadataProperty(name=name))
        else:
            warnings.warn(f"Feature '{name}' has an unsupported type. Skipping. Feature type: {feature_type}")

    if not questions:
        questions.append(LabelQuestion(name="quality", required=True, labels=["good", "bad"]))
        warnings.warn(
            "No questions found in the dataset features. A default question 'quality' with labels ['good', 'bad'] has been added"
        )
        _render_code_snippet(repo_id)

    if not fields:
        raise SettingsError("No fields found in the dataset features. Argilla datasets require at least one field.")

    questions[0].required = True
    fields[0].required = True

    settings = Settings(fields=fields, questions=questions, metadata=metadata)

    return settings


def build_settings_from_repo_id(repo_id: str, feature_mapping: Optional[Dict[str, str]] = None) -> "Settings":
    dataset_features = _get_dataset_features(repo_id)
    return _define_settings_from_features(dataset_features, feature_mapping, repo_id)
