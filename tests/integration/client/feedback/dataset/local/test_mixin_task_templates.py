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

from typing import TYPE_CHECKING

from argilla.client.feedback.dataset import FeedbackDataset
from argilla.client.feedback.schemas import (
    LabelQuestion,
    MultiLabelQuestion,
    RatingQuestion,
    TextQuestion,
)
from argilla.client.feedback.schemas.metadata import TermsMetadataProperty

if TYPE_CHECKING:
    pass


def test_for_question_answering():
    dataset = FeedbackDataset.for_question_answering(
        use_markdown=True, metadata_properties=[TermsMetadataProperty(name="test")]
    )
    assert len(dataset.fields) == 2
    assert len(dataset.questions) == 1
    assert dataset.questions[0].name == "answer"
    assert (
        dataset.questions[0].description == "Answer the question. Note that the answer must exactly be in the context."
    )
    assert dataset.questions[0].required is True
    assert dataset.fields[0].name == "question"
    assert dataset.fields[0].use_markdown is True
    assert dataset.fields[1].name == "context"
    assert dataset.fields[1].use_markdown is True
    assert (
        dataset.guidelines
        == "This is a question answering dataset that contains questions and contexts. Please answer the question by using the context."
    )
    assert dataset.metadata_properties[0].name == "test"


def test_for_text_classification():
    # Test case 1: Single label classification
    dataset = FeedbackDataset.for_text_classification(
        labels=["positive", "negative"], metadata_properties=[TermsMetadataProperty(name="test")]
    )
    assert len(dataset) == 0
    assert dataset.questions[0].name == "label"
    assert (
        dataset.questions[0].description
        == "Classify the text by selecting the correct label from the given list of labels."
    )
    assert isinstance(dataset.questions[0], LabelQuestion)
    assert dataset.questions[0].labels == ["positive", "negative"]
    assert dataset.fields[0].name == "text"
    assert dataset.fields[0].use_markdown is False
    assert (
        dataset.guidelines == "This is a text classification dataset that contains texts and labels. "
        "Given a set of texts and a predefined set of labels, the goal of text classification is to assign one label "
        "to each text based on its content. Please classify the texts by making the correct selection."
    )
    assert dataset.metadata_properties[0].name == "test"

    # Test case 2: Multi-label classification
    dataset = FeedbackDataset.for_text_classification(
        labels=["positive", "negative"], multi_label=True, metadata_properties=[TermsMetadataProperty(name="test")]
    )
    assert len(dataset) == 0
    assert dataset.questions[0].name == "label"
    assert (
        dataset.questions[0].description
        == "Classify the text by selecting the correct label from the given list of labels."
    )
    assert isinstance(dataset.questions[0], MultiLabelQuestion)
    assert dataset.questions[0].labels == ["positive", "negative"]
    assert dataset.fields[0].name == "text"
    assert dataset.fields[0].use_markdown is False
    print(dataset.guidelines)
    assert (
        dataset.guidelines == "This is a text classification dataset that contains texts and labels. "
        "Given a set of texts and a predefined set of labels, the goal of text classification is to assign one "
        "or more labels to each text based on its content. Please classify the texts by making the correct selection."
    )
    assert dataset.metadata_properties[0].name == "test"


def test_for_summarization():
    dataset = FeedbackDataset.for_summarization(
        use_markdown=True, metadata_properties=[TermsMetadataProperty(name="test")]
    )
    assert len(dataset) == 0
    assert dataset.questions[0].name == "summary"
    assert dataset.questions[0].description == "Write a summary of the text."
    assert isinstance(dataset.questions[0], TextQuestion)
    assert dataset.fields[0].name == "text"
    assert dataset.fields[0].use_markdown is True
    assert (
        dataset.guidelines
        == "This is a summarization dataset that contains texts. Please summarize the text in the text field."
    )
    assert dataset.metadata_properties[0].name == "test"


def test_for_supervised_fine_tuning():
    # Test case 1: context=False, use_markdown=False, guidelines=None
    dataset = FeedbackDataset.for_supervised_fine_tuning(
        context=False, use_markdown=False, guidelines=None, metadata_properties=[TermsMetadataProperty(name="test")]
    )
    assert len(dataset) == 0
    assert dataset.questions[0].name == "response"
    assert dataset.questions[0].description == "Write the response to the instruction."
    assert isinstance(dataset.questions[0], TextQuestion)
    assert dataset.questions[0].use_markdown is False
    assert dataset.fields[0].name == "prompt"
    assert dataset.fields[0].use_markdown is False
    assert (
        dataset.guidelines
        == "This is a supervised fine-tuning dataset that contains instructions. Please write the response to the instruction in the response field."
    )
    assert dataset.metadata_properties[0].name == "test"

    # Test case 2: context=True, use_markdown=True, guidelines="Custom guidelines"
    dataset = FeedbackDataset.for_supervised_fine_tuning(
        context=True,
        use_markdown=True,
        guidelines="Custom guidelines",
        metadata_properties=[TermsMetadataProperty(name="test")],
    )
    assert len(dataset) == 0
    assert dataset.questions[0].name == "response"
    assert dataset.questions[0].description == "Write the response to the instruction."
    assert isinstance(dataset.questions[0], TextQuestion)
    assert dataset.questions[0].use_markdown is True
    assert dataset.fields[0].name == "prompt"
    assert dataset.fields[0].use_markdown is True
    assert dataset.fields[1].name == "context"
    assert dataset.fields[1].use_markdown is True
    assert dataset.guidelines == "Custom guidelines"
    assert dataset.metadata_properties[0].name == "test"


def test_for_retrieval_augmented_generation():
    # Test case 1: Single document retrieval augmented generation
    dataset = FeedbackDataset.for_retrieval_augmented_generation(
        number_of_retrievals=1,
        rating_scale=5,
        use_markdown=True,
        metadata_properties=[TermsMetadataProperty(name="test")],
    )
    assert len(dataset) == 0
    assert dataset.questions[0].name == "question_rating_1"
    assert dataset.questions[0].description == "Rate the relevance of the retrieved document."
    assert isinstance(dataset.questions[0], RatingQuestion)
    assert dataset.questions[0].values == [1, 2, 3, 4, 5]
    assert dataset.questions[1].name == "response"
    assert dataset.questions[1].description == "Write the response to the query."
    assert isinstance(dataset.questions[1], TextQuestion)
    assert dataset.fields[0].name == "query"
    assert dataset.fields[0].use_markdown is True
    assert dataset.fields[1].name == "retrieved_document_1"
    assert dataset.fields[1].use_markdown is True
    assert (
        dataset.guidelines
        == "This is a retrieval augmented generation dataset that contains queries and retrieved documents. Please rate the relevancy of retrieved document and write the response to the query in the response field."
    )
    assert dataset.metadata_properties[0].name == "test"

    # Test case 2: Multiple document retrieval augmented generation
    dataset = FeedbackDataset.for_retrieval_augmented_generation(
        number_of_retrievals=3,
        rating_scale=10,
        use_markdown=False,
        guidelines="Custom guidelines",
        metadata_properties=[TermsMetadataProperty(name="test")],
    )
    assert len(dataset) == 0
    assert dataset.questions[0].name == "question_rating_1"
    assert dataset.questions[0].description == "Rate the relevance of the retrieved document."
    assert isinstance(dataset.questions[0], RatingQuestion)
    assert dataset.questions[0].values == list(range(1, 11))
    assert dataset.questions[1].name == "question_rating_2"
    assert dataset.questions[1].description == "Rate the relevance of the retrieved document."
    assert isinstance(dataset.questions[1], RatingQuestion)
    assert dataset.questions[1].values == list(range(1, 11))
    assert dataset.questions[2].name == "question_rating_3"
    assert dataset.questions[2].description == "Rate the relevance of the retrieved document."
    assert isinstance(dataset.questions[2], RatingQuestion)
    assert dataset.questions[2].values == list(range(1, 11))
    assert dataset.questions[3].name == "response"
    assert dataset.questions[3].description == "Write the response to the query."
    assert isinstance(dataset.questions[3], TextQuestion)
    assert dataset.fields[0].name == "query"
    assert dataset.fields[0].use_markdown is False
    assert dataset.fields[1].name == "retrieved_document_1"
    assert dataset.fields[1].use_markdown is False
    assert dataset.fields[2].name == "retrieved_document_2"
    assert dataset.fields[2].use_markdown is False
    assert dataset.fields[3].name == "retrieved_document_3"
    assert dataset.fields[3].use_markdown is False
    assert dataset.guidelines == "Custom guidelines"
    assert dataset.metadata_properties[0].name == "test"


def test_for_sentence_similarity():
    # Test case 1: Default parameters
    dataset = FeedbackDataset.for_sentence_similarity(metadata_properties=[TermsMetadataProperty(name="test")])
    assert len(dataset) == 0
    assert dataset.questions[0].name == "similarity"
    assert dataset.questions[0].description == "Rate the similarity between the two sentences."
    assert isinstance(dataset.questions[0], RatingQuestion)
    assert dataset.questions[0].values == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert dataset.fields[0].name == "sentence1"
    assert dataset.fields[0].use_markdown is False
    assert dataset.fields[1].name == "sentence2"
    assert dataset.fields[1].use_markdown is False
    assert (
        dataset.guidelines
        == "This is a sentence similarity dataset that contains two sentences. Please rate the similarity between the two sentences."
    )
    assert dataset.metadata_properties[0].name == "test"

    # Test case 2: Custom parameters
    dataset = FeedbackDataset.for_sentence_similarity(
        rating_scale=5,
        use_markdown=True,
        guidelines="Custom guidelines",
        metadata_properties=[TermsMetadataProperty(name="test")],
    )
    assert len(dataset) == 0
    assert dataset.questions[0].name == "similarity"
    assert dataset.questions[0].description == "Rate the similarity between the two sentences."
    assert isinstance(dataset.questions[0], RatingQuestion)
    assert dataset.questions[0].values == [1, 2, 3, 4, 5]
    assert dataset.fields[0].name == "sentence1"
    assert dataset.fields[0].use_markdown is True
    assert dataset.fields[1].name == "sentence2"
    assert dataset.fields[1].use_markdown is True
    assert dataset.guidelines == "Custom guidelines"
    assert dataset.metadata_properties[0].name == "test"


def test_for_preference_modeling():
    dataset = FeedbackDataset.for_preference_modeling(
        use_markdown=False, context=True, metadata_properties=[TermsMetadataProperty(name="test")]
    )
    assert len(dataset) == 0
    assert dataset.questions[0].name == "preference"
    assert dataset.questions[0].description == "Choose your preference."
    assert isinstance(dataset.questions[0], LabelQuestion)
    assert dataset.questions[0].labels == ["Response 1", "Response 2"]
    assert dataset.fields[0].name == "prompt"
    assert dataset.fields[0].use_markdown is False
    assert dataset.fields[1].name == "context"
    assert dataset.fields[1].use_markdown is False
    assert dataset.fields[1].required is False
    assert dataset.fields[2].name == "response1"
    assert dataset.fields[2].title == "Response 1"
    assert dataset.fields[2].use_markdown is False
    assert dataset.fields[3].name == "response2"
    assert dataset.fields[3].title == "Response 2"
    assert dataset.fields[3].use_markdown is False
    assert (
        dataset.guidelines
        == "This is a preference dataset that contains contexts and options. Please choose the option that you would prefer in the given context."
    )
    assert dataset.metadata_properties[0].name == "test"


def test_for_natural_language_inference():
    # Test case 1: Default labels and guidelines
    dataset = FeedbackDataset.for_natural_language_inference(metadata_properties=[TermsMetadataProperty(name="test")])
    assert len(dataset) == 0
    assert dataset.questions[0].name == "label"
    assert dataset.questions[0].description == "Choose one of the labels."
    assert isinstance(dataset.questions[0], LabelQuestion)
    assert dataset.questions[0].labels == ["entailment", "neutral", "contradiction"]
    assert dataset.fields[0].name == "premise"
    assert dataset.fields[0].use_markdown is False
    assert dataset.fields[1].name == "hypothesis"
    assert dataset.fields[1].use_markdown is False
    assert (
        dataset.guidelines
        == "This is a natural language inference dataset that contains premises and hypotheses. Please choose the correct label for the given premise and hypothesis."
    )
    assert dataset.metadata_properties[0].name == "test"

    # Test case 2: Custom labels and guidelines
    dataset = FeedbackDataset.for_natural_language_inference(
        labels=["yes", "no"], guidelines="Custom guidelines", metadata_properties=[TermsMetadataProperty(name="test")]
    )
    assert len(dataset) == 0
    assert dataset.questions[0].name == "label"
    assert dataset.questions[0].description == "Choose one of the labels."
    assert isinstance(dataset.questions[0], LabelQuestion)
    assert dataset.questions[0].labels == ["yes", "no"]
    assert dataset.fields[0].name == "premise"
    assert dataset.fields[0].use_markdown is False
    assert dataset.fields[1].name == "hypothesis"
    assert dataset.fields[1].use_markdown is False
    assert dataset.guidelines == "Custom guidelines"
    assert dataset.metadata_properties[0].name == "test"


def test_for_proximal_policy_optimization():
    # Test case 1: Without context and without markdown
    dataset = FeedbackDataset.for_proximal_policy_optimization(metadata_properties=[TermsMetadataProperty(name="test")])
    assert len(dataset) == 0
    assert dataset.questions[0].name == "prompt"
    assert dataset.questions[0].description == "Choose one of the labels that best describes the prompt."
    assert isinstance(dataset.questions[0], LabelQuestion)
    assert dataset.questions[0].labels == ["good", "bad"]
    assert dataset.fields[0].name == "prompt"
    assert dataset.fields[0].use_markdown is False
    assert (
        dataset.guidelines
        == "This is a proximal policy optimization dataset that contains contexts and prompts. Please choose the label that best prompt."
    )
    assert dataset.metadata_properties[0].name == "test"

    # Test case 2: With context and with markdown
    dataset = FeedbackDataset.for_proximal_policy_optimization(
        context=True, use_markdown=True, metadata_properties=[TermsMetadataProperty(name="test")]
    )
    assert len(dataset) == 0
    assert dataset.questions[0].name == "prompt"
    assert dataset.questions[0].description == "Choose one of the labels that best describes the prompt."
    assert isinstance(dataset.questions[0], LabelQuestion)
    assert dataset.questions[0].labels == ["good", "bad"]
    assert dataset.fields[0].name == "prompt"
    assert dataset.fields[0].use_markdown is True
    assert dataset.fields[1].name == "context"
    assert dataset.fields[1].use_markdown is True
    assert (
        dataset.guidelines
        == "This is a proximal policy optimization dataset that contains contexts and prompts. Please choose the label that best prompt."
    )
    assert dataset.metadata_properties[0].name == "test"


def test_for_direct_preference_optimization():
    # Test case 1: Without context and markdown
    dataset = FeedbackDataset.for_direct_preference_optimization(
        metadata_properties=[TermsMetadataProperty(name="test")]
    )
    assert len(dataset) == 0
    assert dataset.questions[0].name == "preference"
    assert dataset.questions[0].description == "Choose the label that is your preference."
    assert isinstance(dataset.questions[0], LabelQuestion)
    assert dataset.questions[0].labels == ["Response 1", "Response 2"]
    assert dataset.fields[0].name == "prompt"
    assert dataset.fields[0].use_markdown is False
    assert dataset.fields[1].name == "response1"
    assert dataset.fields[1].title == "Response 1"
    assert dataset.fields[1].use_markdown is False
    assert dataset.fields[2].name == "response2"
    assert dataset.fields[2].title == "Response 2"
    assert dataset.fields[2].use_markdown is False
    assert (
        dataset.guidelines
        == "This is a direct preference optimization dataset that contains contexts and options. Please choose the option that you would prefer in the given context."
    )
    assert dataset.metadata_properties[0].name == "test"

    # Test case 2: With context and markdown
    dataset = FeedbackDataset.for_direct_preference_optimization(
        context=True, use_markdown=True, metadata_properties=[TermsMetadataProperty(name="test")]
    )
    assert len(dataset) == 0
    assert dataset.questions[0].name == "preference"
    assert dataset.questions[0].description == "Choose the label that is your preference."
    assert isinstance(dataset.questions[0], LabelQuestion)
    assert dataset.questions[0].labels == ["Response 1", "Response 2"]
    assert dataset.fields[0].name == "prompt"
    assert dataset.fields[0].use_markdown is True
    assert dataset.fields[1].name == "context"
    assert dataset.fields[1].use_markdown is True
    assert dataset.fields[2].name == "response1"
    assert dataset.fields[2].title == "Response 1"
    assert dataset.fields[2].use_markdown is True
    assert dataset.fields[3].name == "response2"
    assert dataset.fields[3].title == "Response 2"
    assert dataset.fields[3].use_markdown is True
    assert (
        dataset.guidelines
        == "This is a direct preference optimization dataset that contains contexts and options. Please choose the option that you would prefer in the given context."
    )
    assert dataset.metadata_properties[0].name == "test"
