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

import json
import re
from typing import TYPE_CHECKING, Any, Dict, List

import pytest
from argilla_v1.client.feedback.config import DatasetConfig, DeprecatedDatasetConfig
from argilla_v1.client.feedback.schemas.enums import LabelsOrder
from argilla_v1.client.feedback.schemas.fields import FieldSchema
from argilla_v1.client.feedback.schemas.questions import QuestionSchema
from yaml import SafeLoader, load

if TYPE_CHECKING:
    from argilla_v1.client.feedback.schemas.types import (
        AllowedFieldTypes,
        AllowedMetadataPropertyTypes,
        AllowedQuestionTypes,
    )


def test_dataset_config_yaml(
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
    feedback_dataset_metadata_properties: List["AllowedMetadataPropertyTypes"],
    feedback_dataset_guidelines: str,
) -> None:
    config = DatasetConfig(
        fields=feedback_dataset_fields,
        questions=feedback_dataset_questions,
        metadata_properties=feedback_dataset_metadata_properties,
        guidelines=feedback_dataset_guidelines,
    )
    assert isinstance(config, DatasetConfig)
    assert config.fields == feedback_dataset_fields
    assert config.questions == feedback_dataset_questions
    assert config.metadata_properties == feedback_dataset_metadata_properties
    assert config.guidelines == feedback_dataset_guidelines

    to_yaml_config = config.to_yaml()
    assert isinstance(to_yaml_config, str)
    assert all(f"name: {field.name}" in to_yaml_config for field in feedback_dataset_fields)
    assert all(f"name: {question.name}" in to_yaml_config for question in feedback_dataset_questions)
    assert all(
        f"name: {metadata_property.name}" in to_yaml_config
        for metadata_property in feedback_dataset_metadata_properties
    )
    assert f"guidelines: {feedback_dataset_guidelines}" in to_yaml_config

    assert "!!python/object:uuid.UUID" not in to_yaml_config

    from_yaml_config = DatasetConfig.from_yaml(to_yaml_config)
    assert isinstance(from_yaml_config, DatasetConfig)
    assert from_yaml_config.fields == feedback_dataset_fields
    assert from_yaml_config.questions == feedback_dataset_questions
    assert from_yaml_config.metadata_properties == feedback_dataset_metadata_properties
    assert from_yaml_config.guidelines == feedback_dataset_guidelines


@pytest.mark.usefixtures("feedback_dataset_fields", "feedback_dataset_questions", "feedback_dataset_guidelines")
def test_dataset_config_json_deprecated(
    feedback_dataset_fields: List["AllowedFieldTypes"],
    feedback_dataset_questions: List["AllowedQuestionTypes"],
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


@pytest.mark.parametrize(
    "argilla_version, outdated_config",
    (
        (
            "1.8.0",
            {
                "fields": [
                    {
                        "name": "field-1",
                        "title": "Field-1",
                        "required": True,
                        "settings": {"type": "text", "use_markdown": False},
                        "id": "14585f01-2c97-4756-92cc-cc7af17bc342",
                        "inserted_at": "2023-10-10T16:20:23",
                        "updated_at": "2023-10-10T16:20:23",
                    },
                    {
                        "name": "field-2",
                        "title": "Field-2",
                        "required": False,
                        "settings": {"type": "text", "use_markdown": False},
                        "id": "aaaddedc-a273-478a-a27a-b0970b61a7ef",
                        "inserted_at": "2023-10-10T16:20:23",
                        "updated_at": "2023-10-10T16:20:23",
                    },
                ],
                "questions": [
                    {
                        "name": "question-1",
                        "title": "Question-1",
                        "description": None,
                        "required": True,
                        "settings": {"type": "text", "use_markdown": False},
                        "id": "421982f2-b1e6-4725-91d6-8e8b908a9b6b",
                        "inserted_at": "2023-10-10T16:20:23",
                        "updated_at": "2023-10-10T16:20:23",
                    },
                    {
                        "name": "question-2",
                        "title": "Question-2",
                        "description": None,
                        "required": False,
                        "settings": {
                            "type": "rating",
                            "options": [{"value": 1}, {"value": 2}, {"value": 3}, {"value": 4}, {"value": 5}],
                        },
                        "id": "95f38f77-f4dc-4b1a-9638-1d419359be36",
                        "inserted_at": "2023-10-10T16:20:24",
                        "updated_at": "2023-10-10T16:20:24",
                    },
                ],
                "guidelines": "These are the guidelines",
            },
        ),
        (
            "1.9.0",
            {
                "fields": [
                    {
                        "name": "field-1",
                        "title": "Field-1",
                        "required": True,
                        "settings": {"type": "text", "use_markdown": False},
                        "use_markdown": False,
                        "id": "71b3b494-a8fa-4fb7-98e5-d1d73a3f5f81",
                        "inserted_at": "2023-10-10T16:18:15",
                        "updated_at": "2023-10-10T16:18:15",
                    },
                    {
                        "name": "field-2",
                        "title": "Field-2",
                        "required": False,
                        "settings": {"type": "text", "use_markdown": False},
                        "use_markdown": False,
                        "id": "29ae19df-5fc1-4f65-892f-5bc03df3066b",
                        "inserted_at": "2023-10-10T16:18:15",
                        "updated_at": "2023-10-10T16:18:15",
                    },
                ],
                "questions": [
                    {
                        "name": "question-1",
                        "title": "Question-1",
                        "description": None,
                        "required": True,
                        "settings": {"type": "text", "use_markdown": False},
                        "use_markdown": False,
                        "id": "98672849-651b-4c00-ab2a-7f29087c5b22",
                        "inserted_at": "2023-10-10T16:18:15",
                        "updated_at": "2023-10-10T16:18:15",
                    },
                    {
                        "name": "question-2",
                        "title": "Question-2",
                        "description": None,
                        "required": False,
                        "settings": {
                            "type": "rating",
                            "options": [{"value": 1}, {"value": 2}, {"value": 3}, {"value": 4}, {"value": 5}],
                        },
                        "id": "17ec3e6a-656a-47fa-b016-2f825a7db5a3",
                        "inserted_at": "2023-10-10T16:18:16",
                        "updated_at": "2023-10-10T16:18:16",
                    },
                    {
                        "name": "question-3",
                        "title": "Question-3",
                        "description": None,
                        "required": False,
                        "settings": {
                            "type": "label_selection",
                            "options": [
                                {"value": "label-1", "text": "label-1", "description": None},
                                {"value": "label-2", "text": "label-2", "description": None},
                                {"value": "label-3", "text": "label-3", "description": None},
                            ],
                            "visible_options": 3,
                        },
                        "visible_labels": 20,
                        "id": "857faadf-b65f-4a7f-9336-574c0581aef8",
                        "inserted_at": "2023-10-10T16:18:16",
                        "updated_at": "2023-10-10T16:18:16",
                    },
                    {
                        "name": "question-4",
                        "title": "Question-4",
                        "description": None,
                        "required": False,
                        "settings": {
                            "type": "multi_label_selection",
                            "options": [
                                {"value": "label-1", "text": "label-1", "description": None},
                                {"value": "label-2", "text": "label-2", "description": None},
                                {"value": "label-3", "text": "label-3", "description": None},
                            ],
                            "visible_options": 3,
                            "options_order": LabelsOrder.natural,
                        },
                        "visible_labels": 20,
                        "id": "a3a12c67-73d8-41b6-a697-f88be8f9386c",
                        "inserted_at": "2023-10-10T16:18:16",
                        "updated_at": "2023-10-10T16:18:16",
                    },
                ],
                "guidelines": "These are the guidelines",
            },
        ),
        (
            "1.10.0",
            {
                "fields": [
                    {
                        "name": "field-1",
                        "title": "Field-1",
                        "required": True,
                        "settings": {"type": "text", "use_markdown": False},
                        "use_markdown": False,
                        "id": "f2b70656-4d00-48e5-8309-a45bfd2bfb5a",
                        "inserted_at": "2023-10-10T16:17:05",
                        "updated_at": "2023-10-10T16:17:05",
                    },
                    {
                        "name": "field-2",
                        "title": "Field-2",
                        "required": False,
                        "settings": {"type": "text", "use_markdown": False},
                        "use_markdown": False,
                        "id": "8082835f-446f-4ae5-9e0a-426232eb50b1",
                        "inserted_at": "2023-10-10T16:17:06",
                        "updated_at": "2023-10-10T16:17:06",
                    },
                ],
                "questions": [
                    {
                        "name": "question-1",
                        "title": "Question-1",
                        "description": None,
                        "required": True,
                        "settings": {"type": "text", "use_markdown": False},
                        "use_markdown": False,
                        "id": "d30e8ec1-9c96-4f8a-9cfe-2082738602ad",
                        "inserted_at": "2023-10-10T16:17:06",
                        "updated_at": "2023-10-10T16:17:06",
                    },
                    {
                        "name": "question-2",
                        "title": "Question-2",
                        "description": None,
                        "required": False,
                        "settings": {
                            "type": "rating",
                            "options": [{"value": 1}, {"value": 2}, {"value": 3}, {"value": 4}, {"value": 5}],
                        },
                        "id": "7502637f-ea92-41b7-ae6e-b338494b55dc",
                        "inserted_at": "2023-10-10T16:17:06",
                        "updated_at": "2023-10-10T16:17:06",
                    },
                    {
                        "name": "question-3",
                        "title": "Question-3",
                        "description": None,
                        "required": False,
                        "settings": {
                            "type": "label_selection",
                            "options": [
                                {"value": "label-1", "text": "label-1", "description": None},
                                {"value": "label-2", "text": "label-2", "description": None},
                                {"value": "label-3", "text": "label-3", "description": None},
                            ],
                            "visible_options": 3,
                        },
                        "visible_labels": 20,
                        "id": "43f7242e-a52e-4cd5-9823-82b04d1c38e6",
                        "inserted_at": "2023-10-10T16:17:06",
                        "updated_at": "2023-10-10T16:17:06",
                    },
                    {
                        "name": "question-4",
                        "title": "Question-4",
                        "description": None,
                        "required": False,
                        "settings": {
                            "type": "multi_label_selection",
                            "options": [
                                {"value": "label-1", "text": "label-1", "description": None},
                                {"value": "label-2", "text": "label-2", "description": None},
                                {"value": "label-3", "text": "label-3", "description": None},
                            ],
                            "visible_options": 3,
                            "options_order": LabelsOrder.natural,
                        },
                        "visible_labels": 20,
                        "id": "0fbcf59a-eef9-48d0-b50c-011b22a1b611",
                        "inserted_at": "2023-10-10T16:17:07",
                        "updated_at": "2023-10-10T16:17:07",
                    },
                ],
                "guidelines": "These are the guidelines",
            },
        ),
        (
            "1.11.0",
            {
                "fields": [
                    {
                        "name": "field-1",
                        "title": "Field-1",
                        "required": True,
                        "settings": {"type": "text", "use_markdown": False},
                        "use_markdown": False,
                    },
                    {
                        "name": "field-2",
                        "title": "Field-2",
                        "required": False,
                        "settings": {"type": "text", "use_markdown": False},
                        "use_markdown": False,
                    },
                ],
                "questions": [
                    {
                        "name": "question-1",
                        "title": "Question-1",
                        "description": None,
                        "required": True,
                        "settings": {"type": "text", "use_markdown": False},
                        "use_markdown": False,
                    },
                    {
                        "name": "question-2",
                        "title": "Question-2",
                        "description": None,
                        "required": False,
                        "settings": {
                            "type": "rating",
                            "options": [{"value": 1}, {"value": 2}, {"value": 3}, {"value": 4}, {"value": 5}],
                        },
                        "values": [1, 2, 3, 4, 5],
                    },
                    {
                        "name": "question-3",
                        "title": "Question-3",
                        "description": None,
                        "required": False,
                        "settings": {
                            "type": "label_selection",
                            "options": [
                                {"value": "label-1", "text": "label-1"},
                                {"value": "label-2", "text": "label-2"},
                                {"value": "label-3", "text": "label-3"},
                            ],
                            "visible_options": 3,
                        },
                        "labels": ["label-1", "label-2", "label-3"],
                        "visible_labels": 3,
                    },
                    {
                        "name": "question-4",
                        "title": "Question-4",
                        "description": None,
                        "required": False,
                        "settings": {
                            "type": "multi_label_selection",
                            "options": [
                                {"value": "label-1", "text": "label-1"},
                                {"value": "label-2", "text": "label-2"},
                                {"value": "label-3", "text": "label-3"},
                            ],
                            "visible_options": 3,
                            "options_order": LabelsOrder.natural,
                        },
                        "labels": ["label-1", "label-2", "label-3"],
                        "visible_labels": 3,
                    },
                ],
                "guidelines": "These are the guidelines",
            },
        ),
        (
            "1.12.0",
            {
                "fields": [
                    {
                        "name": "field-1",
                        "title": "Field-1",
                        "required": True,
                        "settings": {"type": "text", "use_markdown": False},
                        "use_markdown": False,
                    },
                    {
                        "name": "field-2",
                        "title": "Field-2",
                        "required": False,
                        "settings": {"type": "text", "use_markdown": False},
                        "use_markdown": False,
                    },
                ],
                "questions": [
                    {
                        "name": "question-1",
                        "title": "Question-1",
                        "description": None,
                        "required": True,
                        "settings": {"type": "text", "use_markdown": False},
                        "use_markdown": False,
                    },
                    {
                        "name": "question-2",
                        "title": "Question-2",
                        "description": None,
                        "required": False,
                        "settings": {
                            "type": "rating",
                            "options": [{"value": 1}, {"value": 2}, {"value": 3}, {"value": 4}, {"value": 5}],
                        },
                        "values": [1, 2, 3, 4, 5],
                    },
                    {
                        "name": "question-3",
                        "title": "Question-3",
                        "description": None,
                        "required": False,
                        "settings": {
                            "type": "label_selection",
                            "options": [
                                {"value": "label-1", "text": "label-1"},
                                {"value": "label-2", "text": "label-2"},
                                {"value": "label-3", "text": "label-3"},
                            ],
                            "visible_options": 3,
                        },
                        "labels": ["label-1", "label-2", "label-3"],
                        "visible_labels": 3,
                    },
                    {
                        "name": "question-4",
                        "title": "Question-4",
                        "description": None,
                        "required": False,
                        "settings": {
                            "type": "multi_label_selection",
                            "options": [
                                {"value": "label-1", "text": "label-1"},
                                {"value": "label-2", "text": "label-2"},
                                {"value": "label-3", "text": "label-3"},
                            ],
                            "visible_options": 3,
                            "options_order": LabelsOrder.natural,
                        },
                        "labels": ["label-1", "label-2", "label-3"],
                        "visible_labels": 3,
                        "labels_order": LabelsOrder.natural,
                    },
                    {
                        "name": "question-5",
                        "title": "Question-5",
                        "description": None,
                        "required": False,
                        "settings": {
                            "type": "ranking",
                            "options": [
                                {"value": "label-1", "text": "label-1"},
                                {"value": "label-2", "text": "label-2"},
                                {"value": "label-3", "text": "label-3"},
                            ],
                        },
                        "values": ["label-1", "label-2", "label-3"],
                    },
                ],
                "guidelines": "These are the guidelines",
            },
        ),
    ),
)
def test_dataset_config_backwards_compatibility_argilla_cfg(
    argilla_version: str, outdated_config: Dict[str, Any]
) -> None:
    print(f"Loading `argilla.cfg` dumped using `push_to_huggingface` from argilla=={argilla_version}")
    config = DeprecatedDatasetConfig.from_json(json.dumps(outdated_config))
    assert isinstance(config, DeprecatedDatasetConfig)

    for field in config.fields:
        assert isinstance(field, FieldSchema)
        matching_field = next(
            (outdated_field for outdated_field in outdated_config["fields"] if outdated_field["name"] == field.name),
            None,
        )
        assert matching_field is not None
        assert field.title == matching_field["title"]
        assert field.required == matching_field["required"]
        if "settings" in matching_field:
            assert field.server_settings == matching_field["settings"]

    for question in config.questions:
        assert isinstance(question, QuestionSchema)
        matching_question = next(
            (
                outdated_question
                for outdated_question in outdated_config["questions"]
                if outdated_question["name"] == question.name
            ),
            None,
        )
        assert matching_question is not None
        assert question.title == matching_question["title"]
        assert question.description == matching_question["description"]
        assert question.required == matching_question["required"]
        if "settings" in matching_question:
            if matching_question["settings"]["type"] in ["label_selection", "multi_label_selection"]:
                _ = [option.pop("description", None) for option in matching_question["settings"]["options"]]
            assert question.server_settings == matching_question["settings"]

    assert config.guidelines == outdated_config["guidelines"]


# Same thing but testing the remaining versions and using YAML as
@pytest.mark.parametrize(
    "argilla_version, outdated_config",
    (
        (
            "1.13.0",
            """
            fields:
            - id: !!python/object:uuid.UUID
                int: 318598997309827170175814937554257429138
              name: field-1
              required: true
              settings:
                type: text
                use_markdown: false
              title: Field-1
              type: text
              use_markdown: false
            - id: !!python/object:uuid.UUID
                int: 69686603559390055136114715170048137456
              name: field-2
              required: false
              settings:
                type: text
                use_markdown: false
              title: Field-2
              type: text
              use_markdown: false
            guidelines: These are the guidelines
            questions:
            - description: null
              id: !!python/object:uuid.UUID
                int: 50048965276074224092389052083005517643
              name: question-1
              required: true
              settings:
                type: text
                use_markdown: false
              title: Question-1
              type: text
              use_markdown: false
            - description: null
              id: !!python/object:uuid.UUID
                int: 41875146250353770121043770832765946446
              name: question-2
              required: false
              settings:
                options:
                - value: 1
                - value: 2
                - value: 3
                - value: 4
                - value: 5
                type: rating
              title: Question-2
              type: rating
              values:
              - 1
              - 2
              - 3
              - 4
              - 5
            - description: null
              id: !!python/object:uuid.UUID
                int: 157923404852454712001576490052121022141
              labels:
              - label-1
              - label-2
              - label-3
              name: question-3
              required: false
              settings:
                options:
                - text: label-1
                  value: label-1
                - text: label-2
                  value: label-2
                - text: label-3
                  value: label-3
                type: label_selection
                visible_options: 3
              title: Question-3
              type: label_selection
              visible_labels: 3
            - description: null
              id: !!python/object:uuid.UUID
                int: 250432660168731216394809741082680978815
              labels:
              - label-1
              - label-2
              - label-3
              name: question-4
              required: false
              settings:
                options:
                - text: label-1
                  value: label-1
                - text: label-2
                  value: label-2
                - text: label-3
                  value: label-3
                type: multi_label_selection
                visible_options: 3
                options_order: natural
              title: Question-4
              type: multi_label_selection
              visible_labels: 3
              labels_order: natural
            - description: null
              id: !!python/object:uuid.UUID
                int: 251163320782812347764238417960223431273
              name: question-5
              required: false
              settings:
                options:
                - text: label-1
                  value: label-1
                - text: label-2
                  value: label-2
                - text: label-3
                  value: label-3
                type: ranking
              title: Question-5
              type: ranking
              values:
              - label-1
              - label-2
              - label-3
            """,
        ),
        (
            "1.14.0,1.15.0,1.16.0",
            """
            fields:
            - name: field-1
              required: true
              settings:
                type: text
                use_markdown: false
              title: Field-1
              type: text
              use_markdown: false
            - name: field-2
              required: false
              settings:
                type: text
                use_markdown: false
              title: Field-2
              type: text
              use_markdown: false
            guidelines: These are the guidelines
            questions:
            - description: null
              name: question-1
              required: true
              settings:
                type: text
                use_markdown: false
              title: Question-1
              type: text
              use_markdown: false
            - description: null
              name: question-2
              required: false
              settings:
                options:
                - value: 1
                - value: 2
                - value: 3
                - value: 4
                - value: 5
                type: rating
              title: Question-2
              type: rating
              values:
              - 1
              - 2
              - 3
              - 4
              - 5
            - description: null
              labels:
              - label-1
              - label-2
              - label-3
              name: question-3
              required: false
              settings:
                options:
                - text: label-1
                  value: label-1
                - text: label-2
                  value: label-2
                - text: label-3
                  value: label-3
                type: label_selection
                visible_options: 3
              title: Question-3
              type: label_selection
              visible_labels: 3
            - description: null
              labels:
              - label-1
              - label-2
              - label-3
              name: question-4
              required: false
              settings:
                options:
                - text: label-1
                  value: label-1
                - text: label-2
                  value: label-2
                - text: label-3
                  value: label-3
                type: multi_label_selection
                visible_options: 3
                options_order: natural
              title: Question-4
              type: multi_label_selection
              visible_labels: 3
              labels_order: natural
            - description: null
              name: question-5
              required: false
              settings:
                options:
                - text: label-1
                  value: label-1
                - text: label-2
                  value: label-2
                - text: label-3
                  value: label-3
                type: ranking
              title: Question-5
              type: ranking
              values:
              - label-1
              - label-2
              - label-3
            """,
        ),
    ),
)
def test_dataset_config_backwards_compatibility_argilla_yaml(argilla_version: str, outdated_config: str) -> None:
    print(f"Loading `argilla.yaml` dumped using `push_to_huggingface` from argilla=={argilla_version}")
    config = DatasetConfig.from_yaml(outdated_config)
    assert isinstance(config, DatasetConfig)

    outdated_config_as_dict = load(
        re.sub(r"(\n\s*|)id: !!python/object:uuid\.UUID\s+int: \d+", "", outdated_config), Loader=SafeLoader
    )
    assert isinstance(outdated_config_as_dict, dict)

    for field in config.fields:
        assert isinstance(field, FieldSchema)
        matching_field = next(
            (
                outdated_field
                for outdated_field in outdated_config_as_dict["fields"]
                if outdated_field["name"] == field.name
            ),
            None,
        )
        assert matching_field is not None
        assert field.title == matching_field["title"]
        assert field.required == matching_field["required"]
        if "settings" in matching_field:
            assert field.server_settings == matching_field["settings"]

    for question in config.questions:
        assert isinstance(question, QuestionSchema)
        matching_question = next(
            (
                outdated_question
                for outdated_question in outdated_config_as_dict["questions"]
                if outdated_question["name"] == question.name
            ),
            None,
        )
        assert matching_question is not None
        assert question.title == matching_question["title"]
        assert question.description == matching_question["description"]
        assert question.required == matching_question["required"]
        if "settings" in matching_question:
            if matching_question["settings"]["type"] in ["label_selection", "multi_label_selection"]:
                _ = [option.pop("description", None) for option in matching_question["settings"]["options"]]
            assert question.server_settings == matching_question["settings"]

    assert config.guidelines == outdated_config_as_dict["guidelines"]
