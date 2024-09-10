import httpx
import warnings
from enum import Enum
from typing import Any, Dict, Optional, TYPE_CHECKING, Union, List

from argilla._exceptions._hub import DatasetsServerException

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


def _get_dataset_features(repo_id: str, config: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """Get the features of a dataset from the datasets server using the repo_id and config.
    Extract the features from the response and return them as a dictionary.

    Parameters:
        repo_id (str): The repository ID of the dataset.
        config (str, optional): The configuration of the dataset. Defaults to None.

    Returns:
        Dict[str, Dict[str, Any]]: The features of the dataset.
    """

    url = f"{DATASETS_SERVER_BASE_URL}/info?dataset={repo_id}"

    try:
        with httpx.Client(timeout=DATASETS_SERVER_TIMEOUT) as client:
            response = client.get(url, headers=DATASETS_SERVER_HEADERS)
            response.raise_for_status()
            response_json = response.json()

            dataset_info = response_json["dataset_info"]
            available_configs = list(dataset_info.keys())

            if len(available_configs) > 1 and config is None:
                warnings.warn("Multiple configurations found. Using the first one.")
                config = available_configs[0]
            elif len(available_configs) == 1:
                config = available_configs[0]
            elif config not in available_configs:
                raise DatasetsServerException(f"Configuration '{config}' not found.")

            features = dataset_info[config]["features"]
            return features

    except (httpx.RequestError, httpx.HTTPStatusError, KeyError) as e:
        raise DatasetsServerException(f"Failed to get dataset info from the datasets server. Error: {str(e)}") from e


def _map_feature_type(feature):
    """Map the feature type to the corresponding FeatureType enum."""

    if isinstance(feature, list) and len(feature) > 0 and isinstance(feature[0], dict):
        sub_features = feature[0]
        if _is_chat_feature(sub_features):
            return FeatureType.CHAT

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


def _define_settings_from_features(features: Union[List[Dict], Dict[str, Any]], config=None) -> "Settings":
    """Define the argilla settings from the features of a dataset.

    Parameters:
        features (Dict[str, Dict[str, Any]): The features of the dataset.
        config (str, optional): The configuration of the dataset. Defaults to None.

    Returns:
        rg.Settings: The settings defined from the features.
    """

    from argilla import ImageField, LabelQuestion, TextQuestion, Settings, TextField

    fields = []
    questions = []
    metadata = []
    mapping = {}

    for name, feature in features.items():
        feature_type = _map_feature_type(feature)

        if feature_type == FeatureType.CHAT:
            # TODO: Implement chat support to create `rg.ChatField`
            # fields.append(rg.ChatField(name=f"{name}_field"))
            # mapping[name] = f"{name}_field"
            pass

        elif feature_type == FeatureType.TEXT:
            fields.append(TextField(name=f"{name}_field"))
            questions.append(TextQuestion(name=f"{name}_question"))
            mapping[name] = (f"{name}_field", f"{name}_question")

        elif feature_type == FeatureType.IMAGE:
            fields.append(ImageField(name=f"{name}_field"))
            mapping[name] = f"{name}_field"

        elif feature_type == FeatureType.LABEL:
            fields.append(TextField(name=f"{name}_field"))
            questions.append(
                LabelQuestion(
                    name=f"{name}_question",
                    labels={str(i): label for i, label in enumerate(feature.get("names", []))},
                )
            )
            mapping[name] = (f"{name}_field", f"{name}_question")

        elif feature_type in [FeatureType.INT, FeatureType.FLOAT]:
            # TODO: Implement metadata support to create `rg.FloatMetadata` or `rg.IntMetadata`
            pass
        else:
            warnings.warn(f"Feature '{name}' has an unsupported type. Skipping. Feature type: {feature_type}")

    settings = Settings(fields=fields, questions=questions, metadata=metadata, mapping=mapping)

    return settings


def build_settings_from_repo_id(repo_id: str, config: str = None):
    dataset_info = _get_dataset_features(repo_id, config)
    return _define_settings_from_features(dataset_info, config)
