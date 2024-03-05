import pytest

from argilla.feedback import SuggestionSchema, TextQuestion


def test_create_suggestion():
    question = TextQuestion(name="text")

    suggestion = SuggestionSchema.with_question_value(question, "Value for text", agent="mock", type="human")

    assert suggestion.question_name == question.name
    assert suggestion.agent == "mock"
    assert suggestion.type == "human"
    assert suggestion.value == "Value for text"


def test_create_suggestion_with_wrong_value():
    with pytest.raises(ValueError, match="Value 10 is not valid for question type text. Expected <class 'str'>."):
        SuggestionSchema.with_question_value(TextQuestion(name="text"), 10, agent="Mock")
