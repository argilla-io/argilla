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

from transformers.tools import (  # noqa
    TextClassificationTool,
    TextQuestionAnsweringTool,
    TextSummarizationTool,
    TranslationTool,
)
from transformers import Tool, HfAgent
from typing import List, Optional, Union


class ArgillaTextClassificationTool(Tool):
    name = "argilla_text_classification_logger"
    description = (
        "This is a tool that logs the inputs and outputs of the `text_classifier` tool to Argilla. ",
        "It always executes, right after each individual `text_classifier` tool. ",
        "For the task `text_classification` it takes `text` and `labels` as inputs. ",
    )

    inputs = ["text", ["text"]]
    outputs = None

    def __call__(self, text: str, labels: Union[str, List[str]]):
        print(f"nText: {text}\nLabel: {labels}")


class ArgillaTextSummarizationTool(Tool):
    name = "argilla_text_summarization_logger"
    description = (
        "This is a tool that logs the inputs and outputs of the `summarizer` tool to Argilla. ",
        "It always executes, right after each individual `summarizer` tool. ",
        "For the task `text_summarization` it takes `text` ands `summarized_text` as inputs. ",
    )

    inputs = ["text", "text"]
    outputs = None

    def __call__(self, text: str, summarized_text: str):
        print(f"nText: {text}\Summarization: {summarized_text}")
        return True


class ArgillaTextTranslationTool(Tool):
    name = "argilla_text_translator_logger"
    description = (
        "This is a tool translation information of `translator` tools to Argilla. ",
        "It always executes, right after each individual `translator` tool. ",
        "It takes `text`, `src_lang`, `tgt_lang` and `translated_text` as inputs. ",
    )

    inputs = ["text", "text"]
    outputs = None

    def __call__(self, text: str, src_lang: str, tgt_lang: str, translated_text: str):
        print(f"nText: {text}\Translated: {translated_text}")


class ArgillaTextQATool(Tool):
    name = "argilla_text_qa_logger"
    description = (
        "This is a tool that logs the inputs and outputs of the `text_qa` tool to Argilla. ",
        "It always executes, right after each individual `text_qa` tool. ",
        "For the task `text_question_answering` it takes `text`, `question` and `answer` as inputs. ",
    )

    inputs = ["text", "text", "text"]
    outputs = None

    def __call__(self, text: str, question, answer: str):
        print(f"nText: {text}\nQuestion: {question}\nAnswer: {answer}")


class ArgillaHFAgent(HfAgent):
    def __init__(self, *args, additional_tools: Optional[List[Tool]] = None, **kwargs):
        if additional_tools is None:
            additional_tools = []
        argilla_text_classification_logger = ArgillaTextClassificationTool()
        argilla_text_summarization_logger = ArgillaTextSummarizationTool()
        argilla_text_translator_logger = ArgillaTextTranslationTool()
        argilla_text_qa_logger = ArgillaTextQATool()
        additional_tools.append(argilla_text_classification_logger)
        additional_tools.append(argilla_text_summarization_logger)
        additional_tools.append(argilla_text_translator_logger)
        additional_tools.append(argilla_text_qa_logger)
        super().__init__(*args, additional_tools=additional_tools, **kwargs)

    def run(self, task, *, return_code=False, remote=False, **kwargs):
        task = task + "\n Log the outputs of intermediate steps Using the Argilla logging tools."
        super().run(task, return_code=return_code, remote=remote, **kwargs)
