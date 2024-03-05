import pytest

from argilla.feedback import TextQuestion, SuggestionBuilder, SuggestionSchema


def test_create_suggestion_from_builder():
    question = TextQuestion(name="text")

    suggestion = SuggestionBuilder().question_value(question, "Value for text").agent("mock").type("human").build()

    assert suggestion.question_name == question.name
    assert suggestion.agent == "mock"
    assert suggestion.type == "human"
    assert suggestion.value == "Value for text"


def test_create_suggestion_with_wrong_value():
    with pytest.raises(ValueError, match="Value 10 is not valid for question type text. Expected <class 'str'>."):
        SuggestionBuilder().question_value(TextQuestion(name="text"), 10).agent("mock").type("human").build()


def test_create_builder_from_suggestion():
    suggestion = SuggestionSchema(question_name="text", value="Value for text", agent="mock", type="human")
    builder = SuggestionBuilder.from_suggestion(suggestion)

    new_suggestion = builder.question_value(TextQuestion(name="other-text"), "Value for other text").build()

    assert new_suggestion.agent == suggestion.agent
    assert new_suggestion.type == suggestion.type
    assert new_suggestion.question_name == "other-text"
    assert new_suggestion.value == "Value for other text"

    assert new_suggestion.question_name != suggestion.question_name
    assert new_suggestion.value != suggestion.value
