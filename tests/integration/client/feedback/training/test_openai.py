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
import re
from typing import TYPE_CHECKING

import argilla as rg
import pytest
from argilla.client.feedback.training.schemas import TrainingTaskForChatCompletionFormat

if TYPE_CHECKING:
    pass


def test_chat_completion():
    dataset = rg.FeedbackDataset.from_huggingface("argilla/customer_assistant")
    # adapation from LlamaIndex's TEXT_QA_PROMPT_TMPL_MSGS[1].content
    user_message_prompt = """Context information is below.
    ---------------------
    {context_str}
    ---------------------
    Given the context information and not prior knowledge but keeping your Argilla Cloud assistant style, answer the query.
    Query: {query_str}
    Answer:
    """
    # adapation from LlamaIndex's TEXT_QA_SYSTEM_PROMPT
    system_prompt = """You are an expert customer service assistant for the Argilla Cloud product that is trusted around the world.
    Always answer the query using the provided context information, and not prior knowledge.
    Some rules to follow:
    1. Never directly reference the given context in your answer.
    2. Avoid statements like 'Based on the context, ...' or 'The context information ...' or anything along those lines.
    """

    def formatting_func(sample: dict):
        from uuid import uuid4

        if sample["response"]:
            chat = str(uuid4())
            user_message = user_message_prompt.format(context_str=sample["context"], query_str=sample["user-message"])
            return [
                (chat, "0", "system", system_prompt),
                (chat, "1", "user", user_message),
                (chat, "2", "assistant", sample["response"][0]["value"]),
            ]
        else:
            return None

    task = rg.feedback.TrainingTask.for_chat_completion(formatting_func=formatting_func)
    rg.feedback.ArgillaTrainer(
        dataset=dataset,
        task=task,
        framework="openai",
    )


def test_training_tas_for_chat_completion():
    dataset = rg.FeedbackDataset.from_huggingface("argilla/customer_assistant")
    # adapation from LlamaIndex's TEXT_QA_PROMPT_TMPL_MSGS[1].content
    user_message_prompt = """Context information is below.
    ---------------------
    {context_str}
    ---------------------
    Given the context information and not prior knowledge but keeping your Argilla Cloud assistant style, answer the query.
    Query: {query_str}
    Answer:
    """
    # adapation from LlamaIndex's TEXT_QA_SYSTEM_PROMPT
    system_prompt = """You are an expert customer service assistant for the Argilla Cloud product that is trusted around the world."""

    def formatting_func(sample: dict):
        from uuid import uuid4

        if sample["response"]:
            chat = str(uuid4())
            user_message = user_message_prompt.format(context_str=sample["context"], query_str=sample["user-message"])
            return [
                (chat, "0", "system", system_prompt),
                (chat, "1", "user", user_message),
                (chat, "2", "assistant", sample["response"][0]["value"]),
            ]
        else:
            return None

    with pytest.raises(
        ValueError,
        match=re.escape(
            f"formatting_func must return {TrainingTaskForChatCompletionFormat.__annotations__['format']}, not <class 'dict'>"
        ),
    ):
        task = rg.feedback.TrainingTask.for_chat_completion(formatting_func=lambda x: {"test": "test"})
        rg.feedback.ArgillaTrainer(
            dataset=dataset,
            task=task,
            framework="openai",
        )

    task = rg.feedback.TrainingTask.for_chat_completion(formatting_func=formatting_func)

    with pytest.raises(
        NotImplementedError, match="Legacy models are not supported for OpenAI with the FeedbackDataset."
    ):
        rg.feedback.ArgillaTrainer(
            dataset=dataset,
            task=task,
            framework="openai",
            model="davinci",
        )

    rg.feedback.ArgillaTrainer(
        dataset=dataset,
        task=task,
        framework="openai",
    )
