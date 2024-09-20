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

import pytest
import argilla as rg

from argilla._exceptions._settings import SettingsError
from argilla.settings._io._hub import _define_settings_from_features


def test_define_settings_from_features_text():
    features = {"text_column": {"_type": "Value", "dtype": "string"}}
    settings = _define_settings_from_features(features, feature_mapping={})

    assert len(settings.fields) == 1
    assert isinstance(settings.fields[0], rg.TextField)
    assert settings.fields[0].name == "text_column"
    assert len(settings.questions) == 1
    assert isinstance(settings.questions[0], rg.TextQuestion)
    assert settings.questions[0].name == "comment"
    assert settings.mapping == {}


def test_define_settings_from_features_image():
    features = {"image_column": {"_type": "Image"}}
    settings = _define_settings_from_features(features, feature_mapping={})

    assert len(settings.fields) == 1
    assert isinstance(settings.fields[0], rg.ImageField)
    assert settings.fields[0].name == "image_column"
    assert len(settings.questions) == 1
    assert settings.questions[0].name == "comment"
    assert settings.mapping == {}


def test_define_settings_from_features_multiple():
    features = {
        "text_column": {"_type": "Value", "dtype": "string"},
        "image_column": {"_type": "Image"},
        "label_column": {"_type": "ClassLabel", "names": ["A", "B"]},
    }
    settings = _define_settings_from_features(features, feature_mapping={})

    assert len(settings.fields) == 2
    assert isinstance(settings.fields[0], rg.TextField)
    assert settings.fields[0].name == "text_column"
    assert isinstance(settings.fields[1], rg.ImageField)
    assert settings.fields[1].name == "image_column"
    assert len(settings.questions) == 1
    assert isinstance(settings.questions[0], rg.LabelQuestion)
    assert settings.questions[0].name == "label_column"
    assert settings.mapping == {}


def test_mapped_question():
    features = {
        "text_column": {"_type": "Value", "dtype": "string"},
        "image_column": {"_type": "Image"},
        "label_column": {"_type": "ClassLabel", "names": ["A", "B"]},
    }
    settings = _define_settings_from_features(features, feature_mapping={"text_column": "question"})

    assert len(settings.fields) == 1
    assert isinstance(settings.fields[0], rg.ImageField)
    assert settings.fields[0].name == "image_column"
    assert len(settings.questions) == 2
    assert isinstance(settings.questions[0], rg.TextQuestion)
    assert settings.questions[0].name == "text_column"
    assert isinstance(settings.questions[1], rg.LabelQuestion)
    assert settings.questions[1].name == "label_column"
    assert settings.mapping == {}


def test_mapped_fields():
    features = {
        "text_column": {"_type": "Value", "dtype": "string"},
        "image_column": {"_type": "Image"},
        "label_column": {"_type": "ClassLabel", "names": ["A", "B"]},
    }
    settings = _define_settings_from_features(features, feature_mapping={"text_column": "field"})

    assert len(settings.fields) == 2
    assert isinstance(settings.fields[0], rg.TextField)
    assert settings.fields[0].name == "text_column"
    assert isinstance(settings.fields[1], rg.ImageField)
    assert settings.fields[1].name == "image_column"
    assert len(settings.questions) == 1
    assert isinstance(settings.questions[0], rg.LabelQuestion)
    assert settings.questions[0].name == "label_column"
    assert settings.mapping == {}


def test_define_settings_from_features_unsupported():
    features = {
        "unsupported_column": {"_type": "Unsupported"},
        "text_field": {"_type": "Value", "dtype": "string"},
        "label_column": {"_type": "ClassLabel", "names": ["A", "B"]},
    }
    with pytest.warns(UserWarning, match="Feature 'unsupported_column' has an unsupported type"):
        settings = _define_settings_from_features(features, feature_mapping={})

    assert len(settings.fields) == 1
    assert len(settings.questions) == 1


def test_define_settings_from_only_label_raises():
    features = {"label_column": {"_type": "ClassLabel", "names": ["A", "B", "C"]}}

    with pytest.raises(SettingsError):
        _define_settings_from_features(features, feature_mapping={})
