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

import argilla as rg
import pytest
from argilla.client.feedback.training.schemas import TrainingTaskForChatCompletionFormat

from tests.integration.client.feedback.helpers import formatting_func_chat_completion


def test_training_task_for_chat_completion(mocked_openai):
    dataset = rg.FeedbackDataset.from_huggingface("argilla/customer_assistant")

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

    task = rg.feedback.TrainingTask.for_chat_completion(formatting_func=formatting_func_chat_completion)

    with pytest.raises(
        NotImplementedError, match="Legacy models are not supported for OpenAI with the FeedbackDataset."
    ):
        rg.feedback.ArgillaTrainer(
            dataset=dataset,
            task=task,
            framework="openai",
            model="davinci",
        )

    trainer = rg.feedback.ArgillaTrainer(
        dataset=dataset,
        task=task,
        framework="openai",
    )
    trainer.train("mock")
