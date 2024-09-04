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

from enum import Enum
from typing import Optional

from datasets import ClassLabel, Features, Value, Sequence, Dataset

from argilla.settings._templates._settings import DefaultSettingsMixin


class FeatureType(Enum):
    document_classification = "document_classification"
    response_ranking = "response_ranking"
    response_rating = "response_rating"


class FeaturePresetsMixin(DefaultSettingsMixin):
    @staticmethod
    def document_classification(labels: list[str]):
        labels.sort()
        return [
            Features(
                {
                    "text": Value("string", id=None),
                    "label": ClassLabel(names=labels, id=None),
                }
            ),
            Features(
                {
                    "document": Value("string"),
                    "sentiment": ClassLabel(names=labels),
                }
            ),
            Features(
                {
                    "content": Value("string"),
                    "category": ClassLabel(names=labels),
                }
            ),
        ]

    @staticmethod
    def response_ranking():
        return [
            Features(
                {
                    "prompt": Value("string"),
                    "chosen": [{"content": Value("string"), "role": Value("string")}],
                    "rejected": [{"content": Value("string"), "role": Value("string")}],
                }
            ),
            Features(
                {
                    "prompt": Value(dtype="string"),
                    "chosen": Sequence(
                        feature={
                            "content": Value(dtype="string"),
                            "role": Value(dtype="string"),
                        }
                    ),
                    "rejected": Sequence(
                        feature={
                            "content": Value(dtype="string"),
                            "role": Value(dtype="string"),
                        }
                    ),
                }
            ),
            Features(
                {
                    "instruction": Value("string"),
                    "input": Value("string"),
                    "response1": Value("string"),
                    "response2": Value("string"),
                }
            ),
            Features(
                {
                    "question": Value("string"),
                    "answer1": Value("string"),
                    "answer2": Value("string"),
                }
            ),
        ]

    @staticmethod
    def response_rating():
        return [
            Features(
                {
                    "instruction": Value("string"),
                    "input": Value("string"),
                    "output": Value("string"),
                }
            ),
            Features(
                {
                    "prompt": Value("string"),
                    "response": Value("string"),
                }
            ),
            Features(
                {
                    "question": Value("string"),
                    "answer": Value("string"),
                }
            ),
        ]

    @staticmethod
    def _compare_features(dataset_features, predefined_features):
        if not set(dataset_features.keys()).issuperset(set(predefined_features.keys())):
            return False

        dataset_features = {k: v for k, v in dataset_features.items() if k in predefined_features}
        return dataset_features == predefined_features

    @classmethod
    def _get_preset(cls, dataset: Dataset, labels: Optional[list[str]] = None):
        if labels is not None and any(
            cls._compare_features(dataset.features, features) for features in cls.document_classification(labels=labels)
        ):
            return FeatureType.document_classification
        elif any(cls._compare_features(dataset.features, features) for features in cls.response_ranking()):
            return FeatureType.response_ranking
        elif any(cls._compare_features(dataset.features, features) for features in cls.response_rating()):
            return FeatureType.response_rating
        else:
            return None

    @classmethod
    def from_dataset(cls, dataset: Dataset, labels: Optional[list[str]] = None):
        feature_preset = cls._get_preset(dataset, labels=labels)
        if feature_preset is None:
            raise ValueError("The dataset features do not match any of the feature presets.")
        elif feature_preset == FeatureType.document_classification:
            return cls.for_document_classification(labels=labels)
        elif feature_preset == FeatureType.response_ranking:
            return cls.for_response_ranking()
        elif feature_preset == FeatureType.response_rating:
            return cls.for_response_rating()
        else:
            raise ValueError(f"Invalid feature preset: {feature_preset}")

    @classmethod
    def from_template(cls, template: str, labels: Optional[list[str]] = None):
        if template == FeatureType.document_classification:
            return cls.for_document_classification(labels=labels)
        elif template == FeatureType.response_ranking:
            return cls.for_response_ranking()
        elif template == FeatureType.response_rating:
            return cls.for_response_rating()
        else:
            raise ValueError(f"Invalid feature preset: {template}. Use one of {FeatureType.__members__.keys()}")
