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

from argilla_v1.client.models import Framework
from argilla_v1.feedback import TrainingTask


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
                {"sentence-1": sample["text"], "sentence-2": sample["text"], "label": 2},
            ]


def formatting_func_sentence_transformers_all_lists(sample: dict):
    labels = [
        annotation["value"]
        for annotation in sample["question-3"]
        if annotation["status"] == "submitted" and annotation["value"] is not None
    ]
    if labels:
        # Force to pass always a list of values
        return [
            {"sentence-1": sample["text"], "sentence-2": sample["text"], "label": 1},
            {"sentence-1": sample["text"], "sentence-2": sample["text"], "label": 2},
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
            return [{"sentence": sample["text"], "label": 1}, {"sentence": sample["text"], "label": 2}]


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
                {"sentence-1": sample["text"], "sentence-2": sample["text"], "sentence-3": sample["text"], "label": 2},
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


def formatting_func_sentence_transformers_rating_question(sample: dict):
    # Formatting function to test the RatingQuestion
    labels = [
        annotation["value"]
        for annotation in sample["question-2"]
        if annotation["status"] == "submitted" and annotation["value"] is not None
    ]
    if labels:
        return {"sentence-1": sample["text"], "sentence-2": sample["text"], "label": labels[0]}


def model_card_pattern(framework: Framework, training_task: Any) -> str:
    # def model_card_pattern() -> str:
    #     def inner(framework: Framework, training_task: Any):
    if framework == Framework("transformers"):
        if training_task == TrainingTask.for_text_classification:
            return TRANSFORMERS_CODE_SNIPPET
        elif training_task == TrainingTask.for_question_answering:
            return TRANSFORMERS_QA_CODE_SNIPPET
    elif framework == Framework("setfit"):
        return SETFIT_CODE_SNIPPET
    elif framework == Framework("peft"):
        return PEFT_CODE_SNIPPET
    elif framework == Framework("spacy"):
        return SPACY_CODE_SNIPPET
    elif framework == Framework("spacy-transformers"):
        return SPACY_TRANSFORMERS_CODE_SNIPPET
    elif framework == Framework("sentence-transformers"):
        return SENTENCE_TRANSFORMERS_CODE_SNIPPET
    elif framework == Framework("trl"):
        if training_task == TrainingTask.for_supervised_fine_tuning:
            return TRL_SFT_CODE_SNIPPET
        elif training_task == TrainingTask.for_reward_modeling:
            return TRL_RM_CODE_SNIPPET
        elif training_task == TrainingTask.for_proximal_policy_optimization:
            return TRL_PPO_CODE_SNIPPET
        elif training_task == TrainingTask.for_direct_preference_optimization:
            return TRL_DPO_CODE_SNIPPET
    elif framework == Framework("openai"):
        return OPENAI_CODE_SNIPPET
    else:
        raise ValueError(f"Framework undefined: {framework}")

    # return inner


SENTENCE_TRANSFORMERS_CODE_SNIPPET = """\
```python
# Load the dataset:
dataset = FeedbackDataset.from_huggingface("argilla/emotion")

# Create the training task:
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
                {"sentence-1": sample["text"], "sentence-2": sample["text"], "label": 2},
            ]

task = TrainingTask.for_sentence_similarity(formatting_func=formatting_func_sentence_transformers)

# Create the ArgillaTrainer:
trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="sentence-transformers",
    model="sentence-transformers/all-MiniLM-L6-v2",
    framework_kwargs={'cross_encoder': False},
)

trainer.update_config({
    "batch_size": 3
})

trainer.train(output_dir="sentence_similarity_model")
```

You can test the type of predictions of this model like so:

```python
trainer.predict(
    [
        ["Machine learning is so easy.", "Deep learning is so straightforward."],
        ["Machine learning is so easy.", "This is so difficult, like rocket science."],
        ["Machine learning is so easy.", "I can't believe how much I struggled with this."]
    ]
)
```
"""


TRANSFORMERS_CODE_SNIPPET = """\
```python
# Load the dataset:
dataset = FeedbackDataset.from_huggingface("argilla/emotion")

# Create the training task:
task = TrainingTask.for_text_classification(text=dataset.field_by_name("text"), label=dataset.question_by_name("question-3"))

# Create the ArgillaTrainer:
trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="transformers",
    model="prajjwal1/bert-tiny",
)

trainer.update_config({
    "logging_steps": 1,
    "num_train_epochs": 1
})

trainer.train(output_dir="text_classification_model")
```
"""


TRANSFORMERS_QA_CODE_SNIPPET = """\
```python
# Load the dataset:
dataset = FeedbackDataset.from_huggingface("argilla/emotion")

# Create the training task:
task = TrainingTask.for_question_answering(question=dataset.field_by_name("label"), context=dataset.field_by_name("text"), answer=dataset.question_by_name("question-1"))

# Create the ArgillaTrainer:
trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="transformers",
    model="prajjwal1/bert-tiny",
)

trainer.update_config({
    "logging_steps": 1,
    "num_train_epochs": 1
})

trainer.train(output_dir="question_answering_model")
```
"""


SETFIT_CODE_SNIPPET = """\
```python
# Load the dataset:
dataset = FeedbackDataset.from_huggingface("argilla/emotion")

# Create the training task:
task = TrainingTask.for_text_classification(text=dataset.field_by_name("text"), label=dataset.question_by_name("question-3"))

# Create the ArgillaTrainer:
trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="setfit",
    model="all-MiniLM-L6-v2",
)

trainer.update_config({
    "num_iterations": 1
})

trainer.train(output_dir="text_classification_model")
```
"""


PEFT_CODE_SNIPPET = """\
```python
# Load the dataset:
dataset = FeedbackDataset.from_huggingface("argilla/emotion")

# Create the training task:
task = TrainingTask.for_text_classification(text=dataset.field_by_name("text"), label=dataset.question_by_name("question-3"))

# Create the ArgillaTrainer:
trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="peft",
    model="prajjwal1/bert-tiny",
)

trainer.train(output_dir="text_classification_model")
"""


SPACY_CODE_SNIPPET = """\
```python
# Load the dataset:
dataset = FeedbackDataset.from_huggingface("argilla/emotion")

# Create the training task:
task = TrainingTask.for_text_classification(text=dataset.field_by_name("text"), label=dataset.question_by_name("question-3"))

# Create the ArgillaTrainer:
trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="spacy",
    lang="en",
    model="en_core_web_sm",
    gpu_id=-1,
    framework_kwargs={'optimize': 'efficiency', 'freeze_tok2vec': False},
)

trainer.train(output_dir="text_classification_model")
```
"""


SPACY_TRANSFORMERS_CODE_SNIPPET = """\
```python
# Load the dataset:
dataset = FeedbackDataset.from_huggingface("argilla/emotion")

# Create the training task:
task = TrainingTask.for_text_classification(text=dataset.field_by_name("text"), label=dataset.question_by_name("question-3"))

# Create the ArgillaTrainer:
trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="spacy-transformers",
    lang="en",
    model="prajjwal1/bert-tiny",
    gpu_id=-1,
    framework_kwargs={'optimize': 'efficiency', 'update_transformer': True},
)

trainer.train(output_dir="text_classification_model")
```
"""


OPENAI_CODE_SNIPPET = """\
```python
# Load the dataset:
dataset = FeedbackDataset.from_huggingface("argilla/emotion")

# Create the training task:
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

task = TrainingTask.for_chat_completion(formatting_func=formatting_func_chat_completion)

# Create the ArgillaTrainer:
trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="openai",
)

trainer.train(output_dir="chat_completion_model")
```

You can test the type of predictions of this model like so:

```python
# After training we can use the model from the openai framework, you can take a look at their docs in order to use the model
import openai

completion = openai.ChatCompletion.create(
    model="ft:gpt-3.5-turbo:my-org:custom_suffix:id",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)

```
"""


TRL_SFT_CODE_SNIPPET = """\
```python
# Load the dataset:
dataset = FeedbackDataset.from_huggingface("argilla/emotion")

# Create the training task:
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
        return f"### Text\\n{sample['text']}"
    return None

task = TrainingTask.for_supervised_fine_tuning(formatting_func=formatting_func_sft)

# Create the ArgillaTrainer:
trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="trl",
    model="sshleifer/tiny-gpt2",
)

trainer.update_config({
    "evaluation_strategy": "no",
    "max_steps": 1
})

trainer.train(output_dir="sft_model")
```

You can test the type of predictions of this model like so:

```python
# This type of model has no `predict` method implemented from argilla, but can be done using the underlying library
from transformers import GenerationConfig, AutoTokenizer, GPT2LMHeadModel

def generate(model_id: str, instruction: str, context: str = "") -> str:
    model = GPT2LMHeadModel.from_pretrained(model_id)
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    inputs = template.format(
        instruction=instruction,
        context=context,
        response="",
    ).strip()

    encoding = tokenizer([inputs], return_tensors="pt")
    outputs = model.generate(
        **encoding,
        generation_config=GenerationConfig(
            max_new_tokens=32,
            min_new_tokens=12,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        ),
    )
    return tokenizer.decode(outputs[0])

generate("sft_model", "Is a toad a frog?")
```
"""


TRL_RM_CODE_SNIPPET = """\
```python
# Load the dataset:
dataset = FeedbackDataset.from_huggingface("argilla/emotion")

# Create the training task:
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

task = TrainingTask.for_reward_modeling(formatting_func=formatting_func_rm)

# Create the ArgillaTrainer:
trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="trl",
    model="sshleifer/tiny-gpt2",
)

trainer.update_config({
    "evaluation_strategy": "no",
    "max_steps": 1
})

trainer.train(output_dir="rm_model")
```

You can test the type of predictions of this model like so:

```python
# This type of model has no `predict` method implemented from argilla, but can be done using the underlying library
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model = AutoModelForSequenceClassification.from_pretrained("rm_model")
tokenizer = AutoTokenizer.from_pretrained("rm_model")

def get_score(model, tokenizer, text):
    # Tokenize the input sequences
    inputs = tokenizer(text, truncation=True, padding="max_length", max_length=512, return_tensors="pt")

    # Perform forward pass
    with torch.no_grad():
        outputs = model(**inputs)

    # Extract the logits
    return outputs.logits[0, 0].item()

# Example usage
example = template.format(instruction="your prompt", context="your context", response="response")

score = get_score(model, tokenizer, example)
print(score)
```
"""


TRL_PPO_CODE_SNIPPET = """\
```python
# Load the dataset:
dataset = FeedbackDataset.from_huggingface("argilla/emotion")

# Create the training task:
def formatting_func_ppo(sample: Dict[str, Any]):
    return sample["text"]

task = TrainingTask.for_proximal_policy_optimization(formatting_func=formatting_func_ppo)

# Create the ArgillaTrainer:
trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="trl",
    model="sshleifer/tiny-gpt2",
)

trainer.train(output_dir="ppo_model")
```

You can test the type of predictions of this model like so:

```python
# This type of model has no `predict` method implemented from argilla, but can be done using the underlying library
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("ppo_model")
tokenizer = AutoTokenizer.from_pretrained("ppo_model")
tokenizer.pad_token = tokenizer.eos_token

inputs = template.format(
    instruction="your prompt",
    context="your context",
    response=""
).strip()
encoding = tokenizer([inputs], return_tensors="pt")
outputs = model.generate(**encoding, max_new_tokens=30)
output_text = tokenizer.decode(outputs[0])
print(output_text)
```
"""


TRL_DPO_CODE_SNIPPET = """\
```python
# Load the dataset:
dataset = FeedbackDataset.from_huggingface("argilla/emotion")

# Create the training task:
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

task = TrainingTask.for_direct_preference_optimization(formatting_func=formatting_func_dpo)

# Create the ArgillaTrainer:
trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="trl",
    model="sshleifer/tiny-gpt2",
)

trainer.update_config({
    "evaluation_strategy": "no",
    "max_steps": 1
})

trainer.train(output_dir="dpo_model")
```

You can test the type of predictions of this model like so:

```python
# This type of model has no `predict` method implemented from argilla, but can be done using the underlying library
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("dpo_model")
tokenizer = AutoTokenizer.from_pretrained("dpo_model")
tokenizer.pad_token = tokenizer.eos_token

inputs = template.format(
    instruction="your prompt",
    context="your context",
    response=""
).strip()
encoding = tokenizer([inputs], return_tensors="pt")
outputs = model.generate(**encoding, max_new_tokens=30)
output_text = tokenizer.decode(outputs[0])
print(output_text)
```
"""
