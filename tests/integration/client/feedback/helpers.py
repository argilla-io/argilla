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

"""This module contains primarily formatting functions used to prepare the datasets
for the trainer that may be reused in different modules.
"""

from collections import Counter
from typing import Any, Dict, Iterator


def formatting_func_sft(sample: Dict[str, Any]) -> Iterator[str]:
    # For example, the sample must be most frequently rated as "1" in question-2 and
    # label "b" from "question-3" must have not been set by any annotator
    ratings = [
        annotation["value"]
        for annotation in sample["question-2"]
        if annotation["status"] == "submitted" and annotation["value"] is not None
    ]
    labels = [
        annotation["value"]
        for annotation in sample["question-3"]
        if annotation["status"] == "submitted" and annotation["value"] is not None
    ]
    if ratings and Counter(ratings).most_common(1)[0][0] == 1 and "b" not in labels:
        return f"### Text\n{sample['text']}"
    return None


def formatting_func_rm(sample: Dict[str, Any]):
    # The FeedbackDataset isn't really set up for RM, so we'll just use an arbitrary example here
    labels = [
        annotation["value"]
        for annotation in sample["question-3"]
        if annotation["status"] == "submitted" and annotation["value"] is not None
    ]
    if labels:
        # Three cases for the tests: None, one tuple and yielding multiple tuples
        if labels[0] == "a":
            return None
        elif labels[0] == "b":
            return sample["text"], sample["text"][:5]
        elif labels[0] == "c":
            return [(sample["text"], sample["text"][5:10]), (sample["text"], sample["text"][:5])]


def formatting_func_ppo(sample: Dict[str, Any]):
    return sample["text"]


def formatting_func_dpo(sample: Dict[str, Any]):
    # The FeedbackDataset isn't really set up for DPO, so we'll just use an arbitrary example here
    labels = [
        annotation["value"]
        for annotation in sample["question-3"]
        if annotation["status"] == "submitted" and annotation["value"] is not None
    ]
    if labels:
        # Three cases for the tests: None, one tuple and yielding multiple tuples
        if labels[0] == "a":
            return None
        elif labels[0] == "b":
            return sample["text"][::-1], sample["text"], sample["text"][:5]
        elif labels[0] == "c":
            return [
                (sample["text"], sample["text"][::-1], sample["text"][:5]),
                (sample["text"][::-1], sample["text"], sample["text"][:5]),
            ]


user_message_prompt = """Context information is below.
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge but keeping your Argilla Cloud assistant style, answer the query.
Query: {query_str}
Answer:
"""
# adapation from LlamaIndex's TEXT_QA_SYSTEM_PROMPT
system_prompt = (
    """You are an expert customer service assistant for the Argilla Cloud product that is trusted around the world."""
)


def formatting_func_chat_completion(sample: dict):
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


def formatting_func_sentence_transformers(sample: dict):
    labels = [
        annotation["value"]
        for annotation in sample["question-3"]
        if annotation["status"] == "submitted" and annotation["value"] is not None
    ]
    if labels:
        # Three cases for the tests: None, one tuple and yielding multiple tuples
        if labels[0] == "a":
            return None
        elif labels[0] == "b":
            return {"sentence-1": sample["text"], "sentence-2": sample["text"], "label": 1}
        elif labels[0] == "c":
            return [
                {"sentence-1": sample["text"], "sentence-2": sample["text"], "label": 1},
                {"sentence-1": sample["text"], "sentence-2": sample["text"], "label": 0},
            ]


# Additional formatting functions used for different sentence transformer cases:


def formatting_func_sentence_transformers_case_1_b(sample):
    labels = [
        annotation["value"]
        for annotation in sample["question-3"]
        if annotation["status"] == "submitted" and annotation["value"] is not None
    ]
    if labels:
        if labels[0] == "a":
            return None
        elif labels[0] == "b":
            return {"sentence-1": sample["text"], "sentence-2": sample["text"], "label": 0.786}
        elif labels[0] == "c":
            return [
                {"sentence-1": sample["text"], "sentence-2": sample["text"], "label": 0.786},
                {"sentence-1": sample["text"], "sentence-2": sample["text"], "label": 0.56},
            ]


def formatting_func_sentence_transformers_case_2(sample):
    labels = [
        annotation["value"]
        for annotation in sample["question-3"]
        if annotation["status"] == "submitted" and annotation["value"] is not None
    ]
    if labels:
        # Three cases for the tests: None, one tuple and yielding multiple tuples
        if labels[0] == "a":
            return None
        elif labels[0] == "b":
            return {"sentence-1": sample["text"], "sentence-2": sample["text"]}
        elif labels[0] == "c":
            return [{"sentence-1": sample["text"], "sentence-2": sample["text"]}] * 2


def formatting_func_sentence_transformers_case_3_a(sample):
    labels = [
        annotation["value"]
        for annotation in sample["question-3"]
        if annotation["status"] == "submitted" and annotation["value"] is not None
    ]
    if labels:
        # Three cases for the tests: None, one tuple and yielding multiple tuples
        if labels[0] == "a":
            return None
        elif labels[0] == "b":
            return {"sentence": sample["text"], "label": 1}
        elif labels[0] == "c":
            return [{"sentence": sample["text"], "label": 1}, {"sentence": sample["text"], "label": 0}]


def formatting_func_sentence_transformers_case_3_b(sample):
    labels = [
        annotation["value"]
        for annotation in sample["question-3"]
        if annotation["status"] == "submitted" and annotation["value"] is not None
    ]
    if labels:
        if labels[0] == "a":
            return None
        elif labels[0] == "b":
            return {
                "sentence-1": sample["text"],
                "sentence-2": sample["text"],
                "sentence-3": sample["text"],
                "label": 1,
            }
        elif labels[0] == "c":
            return [
                {"sentence-1": sample["text"], "sentence-2": sample["text"], "sentence-3": sample["text"], "label": 1},
                {"sentence-1": sample["text"], "sentence-2": sample["text"], "sentence-3": sample["text"], "label": 0},
            ]


def formatting_func_sentence_transformers_case_4(sample):
    labels = [
        annotation["value"]
        for annotation in sample["question-3"]
        if annotation["status"] == "submitted" and annotation["value"] is not None
    ]
    if labels:
        if labels[0] == "a":
            return None
        elif labels[0] == "b":
            return {"sentence-1": sample["text"], "sentence-2": sample["text"], "sentence-3": sample["text"]}
        elif labels[0] == "c":
            return [{"sentence-1": sample["text"], "sentence-2": sample["text"], "sentence-3": sample["text"]}] * 2
