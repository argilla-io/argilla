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

from typing import Callable

import pytest
from argilla.client.feedback.dataset import FeedbackDataset
from argilla.client.feedback.schemas import (
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
    TextQuestion,
)
from argilla.client.feedback.schemas.metadata import TermsMetadataProperty

parametrized_task_templates = {
    "for_question_anwsering": (
        FeedbackDataset.for_question_answering(
            use_markdown=True, metadata_properties=[TermsMetadataProperty(name="test")]
        ),
        "This is a question answering dataset",
        True,
        2,
        [TextQuestion],
    ),
    "for_text_classification_1": (
        FeedbackDataset.for_text_classification(
            labels=["positive", "negative"], metadata_properties=[TermsMetadataProperty(name="test")]
        ),
        "This is a text classification",
        False,
        1,
        [LabelQuestion],
    ),
    "for_text_classification_2": (
        FeedbackDataset.for_text_classification(
            labels=["positive", "negative"], multi_label=True, metadata_properties=[TermsMetadataProperty(name="test")]
        ),
        "This is a text classification",
        False,
        1,
        [MultiLabelQuestion],
    ),
    "for_summarization": (
        FeedbackDataset.for_summarization(use_markdown=True, metadata_properties=[TermsMetadataProperty(name="test")]),
        "This is a summarization",
        True,
        1,
        [TextQuestion],
    ),
    "for_supervised_fine_tuning_1": (
        FeedbackDataset.for_supervised_fine_tuning(
            context=False, use_markdown=False, guidelines=None, metadata_properties=[TermsMetadataProperty(name="test")]
        ),
        "This is a supervised fine-tuning",
        False,
        1,
        [TextQuestion],
    ),
    "for_supervised_fine_tuning_2": (
        FeedbackDataset.for_supervised_fine_tuning(
            context=True,
            use_markdown=True,
            guidelines="Custom guidelines",
            metadata_properties=[TermsMetadataProperty(name="test")],
        ),
        "Custom guidelines",
        True,
        2,
        [TextQuestion],
    ),
    "for_retrieval_augmented_generation_1": (
        FeedbackDataset.for_retrieval_augmented_generation(
            number_of_retrievals=1,
            rating_scale=5,
            use_markdown=True,
            metadata_properties=[TermsMetadataProperty(name="test")],
        ),
        "This is a retrieval augmented",
        True,
        2,
        [RatingQuestion, TextQuestion],
    ),
    "for_retrieval_augmented_generation_2": (
        FeedbackDataset.for_retrieval_augmented_generation(
            number_of_retrievals=3,
            rating_scale=10,
            use_markdown=False,
            guidelines="Custom guidelines",
            metadata_properties=[TermsMetadataProperty(name="test")],
        ),
        "Custom guidelines",
        False,
        4,
        [RatingQuestion, RatingQuestion, RatingQuestion, TextQuestion],
    ),
    "for_sentence_similarity_1": (
        FeedbackDataset.for_sentence_similarity(metadata_properties=[TermsMetadataProperty(name="test")]),
        "This is a sentence similarity",
        False,
        2,
        [RatingQuestion],
    ),
    "for_sentence_similarity_2": (
        FeedbackDataset.for_sentence_similarity(
            rating_scale=5,
            use_markdown=True,
            guidelines="Custom guidelines",
            metadata_properties=[TermsMetadataProperty(name="test")],
        ),
        "Custom guidelines",
        True,
        2,
        [RatingQuestion],
    ),
    "for_preference_modeling": (
        FeedbackDataset.for_preference_modeling(
            use_markdown=False, context=True, metadata_properties=[TermsMetadataProperty(name="test")]
        ),
        "This is a preference dataset",
        False,
        4,
        [RankingQuestion],
    ),
    "for_natural_language_inference_1": (
        FeedbackDataset.for_natural_language_inference(metadata_properties=[TermsMetadataProperty(name="test")]),
        "This is a natural language inference",
        False,
        2,
        [LabelQuestion],
    ),
    "for_natural_language_inference_2": (
        FeedbackDataset.for_natural_language_inference(
            labels=["yes", "no"],
            guidelines="Custom guidelines",
            metadata_properties=[TermsMetadataProperty(name="test")],
        ),
        "Custom guidelines",
        False,
        2,
        [LabelQuestion],
    ),
    "for_proximal_policy_optimization_1": (
        FeedbackDataset.for_proximal_policy_optimization(metadata_properties=[TermsMetadataProperty(name="test")]),
        "This is a proximal policy optimization",
        False,
        1,
        [RatingQuestion],
    ),
    "for_proximal_policy_optimization_2": (
        FeedbackDataset.for_proximal_policy_optimization(
            context=True, use_markdown=True, metadata_properties=[TermsMetadataProperty(name="test")]
        ),
        "This is a proximal policy optimization",
        True,
        2,
        [RatingQuestion],
    ),
    "for_direct_preference_optimization_1": (
        FeedbackDataset.for_direct_preference_optimization(metadata_properties=[TermsMetadataProperty(name="test")]),
        "This is a direct preference optimization",
        False,
        3,
        [RankingQuestion],
    ),
    "for_direct_preference_optimization_2": (
        FeedbackDataset.for_direct_preference_optimization(
            context=True, use_markdown=True, metadata_properties=[TermsMetadataProperty(name="test")]
        ),
        "This is a direct preference optimization",
        True,
        4,
        [RankingQuestion],
    ),
    "for_multi_modal_classification_1": (
        FeedbackDataset.for_multi_modal_classification(
            labels=["video", "audio", "image"], metadata_properties=[TermsMetadataProperty(name="test")]
        ),
        "This is a multi-modal classification",
        True,
        1,
        [LabelQuestion],
    ),
    "for_multi_modal_classification_2": (
        FeedbackDataset.for_multi_modal_classification(
            labels=["video", "audio", "image"],
            multi_label=True,
            metadata_properties=[TermsMetadataProperty(name="test")],
        ),
        "This is a multi-modal classification",
        True,
        1,
        [MultiLabelQuestion],
    ),
    "for_multi_modal_transcription": (
        FeedbackDataset.for_multi_modal_transcription(
            use_markdown_question=True,
            guidelines="Custom guidelines",
            metadata_properties=[TermsMetadataProperty(name="test")],
        ),
        "Custom guidelines",
        True,
        1,
        [TextQuestion],
    ),
}


@pytest.mark.parametrize(
    "dataset, guidelines_start, use_markdown, number_of_fields, question_types",
    [
        parametrized_task_templates["for_question_anwsering"],
        parametrized_task_templates["for_text_classification_1"],
        parametrized_task_templates["for_text_classification_2"],
        parametrized_task_templates["for_summarization"],
        parametrized_task_templates["for_supervised_fine_tuning_1"],
        parametrized_task_templates["for_supervised_fine_tuning_2"],
        parametrized_task_templates["for_retrieval_augmented_generation_1"],
        parametrized_task_templates["for_retrieval_augmented_generation_2"],
        parametrized_task_templates["for_sentence_similarity_1"],
        parametrized_task_templates["for_sentence_similarity_2"],
        parametrized_task_templates["for_preference_modeling"],
        parametrized_task_templates["for_proximal_policy_optimization_1"],
        parametrized_task_templates["for_proximal_policy_optimization_2"],
        parametrized_task_templates["for_direct_preference_optimization_1"],
        parametrized_task_templates["for_direct_preference_optimization_2"],
        parametrized_task_templates["for_multi_modal_classification_1"],
        parametrized_task_templates["for_multi_modal_classification_2"],
        parametrized_task_templates["for_multi_modal_transcription"],
    ],
)
def test_task_templates(
    dataset: FeedbackDataset, guidelines_start: str, use_markdown: bool, number_of_fields: int, question_types: Callable
):
    assert len(dataset) == 0
    assert len(dataset.fields) == number_of_fields
    assert len(dataset.questions) == len(question_types)
    assert dataset.guidelines.startswith(guidelines_start)
    for field in dataset.fields:
        assert field.use_markdown is use_markdown
    for question, question_type in zip(dataset.questions, question_types):
        assert isinstance(question, question_type)
    for metadata in dataset.metadata_properties:
        assert metadata == TermsMetadataProperty(name="test")
