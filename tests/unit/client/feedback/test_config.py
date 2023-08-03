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

from typing import TYPE_CHECKING, List

import pytest
from argilla.client.feedback.config import DatasetConfig, DeprecatedDatasetConfig

if TYPE_CHECKING:
    from argilla.client.feedback.schemas import FieldSchema, QuestionSchema


@pytest.mark.usefixtures("feedback_dataset_fields", "feedback_dataset_questions", "feedback_dataset_guidelines")
def test_dataset_config_yaml(
    feedback_dataset_fields: List["FieldSchema"],
    feedback_dataset_questions: List["QuestionSchema"],
    feedback_dataset_guidelines: str,
) -> None:
    config = DatasetConfig(
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
        guidelines=feedback_dataset_guidelines,
    )
    assert isinstance(config, DatasetConfig)
    assert config.fields == feedback_dataset_fields
    assert config.questions == feedback_dataset_questions
    assert config.guidelines == feedback_dataset_guidelines

    to_yaml_config = config.to_yaml()
    assert isinstance(to_yaml_config, str)
    assert all(f"name: {field.name}" in to_yaml_config for field in feedback_dataset_fields)
    assert all(f"name: {question.name}" in to_yaml_config for question in feedback_dataset_questions)
    assert f"guidelines: {feedback_dataset_guidelines}" in to_yaml_config

    assert "!!python/object:uuid.UUID" not in to_yaml_config

    from_yaml_config = DatasetConfig.from_yaml(to_yaml_config)
    assert isinstance(from_yaml_config, DatasetConfig)
    assert from_yaml_config.fields == feedback_dataset_fields
    assert all(field.id is None for field in from_yaml_config.fields)
    assert from_yaml_config.questions == feedback_dataset_questions
    assert all(question.id is None for question in from_yaml_config.questions)
    assert from_yaml_config.guidelines == feedback_dataset_guidelines


@pytest.mark.usefixtures("feedback_dataset_fields", "feedback_dataset_questions", "feedback_dataset_guidelines")
def test_dataset_config_json_deprecated(
    feedback_dataset_fields: List["FieldSchema"],
    feedback_dataset_questions: List["QuestionSchema"],
    feedback_dataset_guidelines: str,
) -> None:
    config = DeprecatedDatasetConfig(
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
        guidelines=feedback_dataset_guidelines,
    )
    assert isinstance(config, DeprecatedDatasetConfig)
    assert config.fields == feedback_dataset_fields
    assert config.questions == feedback_dataset_questions
    assert config.guidelines == feedback_dataset_guidelines

    with pytest.warns(DeprecationWarning, match="`DatasetConfig` can just be dumped to YAML"):
        to_json_config = config.to_json()
    assert isinstance(to_json_config, str)
    assert all(f'"name": "{field.name}"' in to_json_config for field in feedback_dataset_fields)
    assert all(f'"name": "{question.name}"' in to_json_config for question in feedback_dataset_questions)
    assert f'"guidelines": "{feedback_dataset_guidelines}"' in to_json_config

    with pytest.warns(DeprecationWarning, match="`DatasetConfig` can just be loaded from YAML"):
        from_json_config = config.from_json(to_json_config)
    assert isinstance(from_json_config, DeprecatedDatasetConfig)
    assert from_json_config.fields == feedback_dataset_fields
    assert from_json_config.questions == feedback_dataset_questions
    assert from_json_config.guidelines == feedback_dataset_guidelines
