import pytest
import argilla as rg
from argilla._helpers._datasets_server import _define_settings_from_features, FeatureType


def test_define_settings_from_features_text():
    features = {"text_column": {"_type": "Value", "dtype": "string"}}
    settings = _define_settings_from_features(features)

    assert len(settings.fields) == 1
    assert isinstance(settings.fields[0], rg.TextField)
    assert len(settings.questions) == 1
    assert isinstance(settings.questions[0], rg.TextQuestion)
    assert settings.mapping == {"text_column": ("text_column_field", "text_column_question")}


def test_define_settings_from_features_image():
    features = {"image_column": {"_type": "Image"}}
    settings = _define_settings_from_features(features)

    assert len(settings.fields) == 1
    assert isinstance(settings.fields[0], rg.ImageField)
    assert len(settings.questions) == 0
    assert settings.mapping == {"image_column": "image_column_field"}


def test_define_settings_from_features_label():
    features = {"label_column": {"_type": "ClassLabel", "names": ["A", "B", "C"]}}
    settings = _define_settings_from_features(features)

    assert len(settings.fields) == 1
    assert isinstance(settings.fields[0], rg.TextField)
    assert len(settings.questions) == 1
    assert isinstance(settings.questions[0], rg.LabelQuestion)
    assert settings.questions[0].labels == ["0", "1", "2"]
    assert settings.mapping == {"label_column": ("label_column_field", "label_column_question")}



def test_define_settings_from_features_multiple():
    features = {
        "text_column": {"_type": "Value", "dtype": "string"},
        "image_column": {"_type": "Image"},
        "label_column": {"_type": "ClassLabel", "names": ["A", "B"]},
    }
    settings = _define_settings_from_features(features)

    assert len(settings.fields) == 3
    assert len(settings.questions) == 2
    assert len(settings.mapping) == 3


def test_define_settings_from_features_unsupported():
    features = {"unsupported_column": {"_type": "Unsupported"}}
    with pytest.warns(UserWarning, match="Feature 'unsupported_column' has an unsupported type"):
        settings = _define_settings_from_features(features)

    assert len(settings.fields) == 0
    assert len(settings.questions) == 0
    assert len(settings.mapping) == 0
