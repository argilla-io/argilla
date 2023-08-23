# Fine-tune an LLM

After [collecting the responses](./collect_responses.html) from our `FeedbackDataset` we can start fine-tuning our LLM. Due to the customizability of the task, this might require setting up a custom post-processing workflow but we will provide some good toy examples for the [classic LLM approaches](../conceptual_guides/rlhf.html): pre-training, supervised fine-tuning, reward modeling, and reinforcement learning.

## Supervised finetuning

The goal of Supervised Fine Tuning (SFT) is to optimize this pre-trained model to generate the responses that users are looking for. After pre-training a causal language model, it can generate feasible human text, but it will not be able to have proper `answers` to `question` phrases posed by the user in a conversational or instruction set. Therefore, we need to collect and curate data tailored to this use case to teach the model to mimic this data. We have a section in our docs about [collecting data for this task](../conceptual_guides/sft.html) and there are many good [pre-trained causal language models](https://huggingface.co/models?pipeline_tag=text-generation&sort=downloads) available on Hugging Face.

### Data

Data for the training phase is generally divided into two different types generic for domain-like finetuning or chat for fine-tuning an instruction set.

#### Generic

In a generic fine-tuning setting, the aim is to make the model more proficient in generating coherent and contextually appropriate text within a particular domain. For example, if we want the model to generate text related to medical research, we would fine-tune it using a dataset consisting of medical literature, research papers, or related documents. By exposing the model to domain-specific data during training, it becomes more knowledgeable about the terminology, concepts, and writing style prevalent in that domain. This enables the model to generate more accurate and contextually appropriate responses when prompted with queries or tasks related to the specific domain. An example of this format is the [PubMed data](https://huggingface.co/datasets/pubmed), but it might be smart to add some nuance by generic instruction phrases that indicate the scope of the data, like `Generate a medical paper abstract: ...`.

```bash
# Five distinct ester hydrolases (EC 3-1) have been characterized in guinea-pig epidermis. These are carboxylic esterase, acid phosphatase, pyrophosphatase, and arylsulphatase A and B. Their properties are consistent with those of lysosomal enzymes.
```

#### Chat

On the other hand, instruction-based fine-tuning involves training the model to understand and respond to specific instructions or prompts given by the user. This approach allows for greater control and specificity in the generated output. For example, if we want the model to summarize a given text, we can fine-tune it using a dataset that consists of pairs of text passages and their corresponding summaries. The model can then be instructed to generate a summary based on a given input text. By fine-tuning the model in this manner, it becomes more adept at following instructions and producing output that aligns with the desired task or objective. An example of this format used is our [curated Dolly dataset](https://huggingface.co/datasets/argilla/databricks-dolly-15k-curated-en) with `instruction`, `context` and `response` fields. However, we can also have simpler datasets with only `question` and `answer` fields.

::::{tab-set}

:::{tab-item} Template

```bash
### Instruction
{instruction}

### Context
{context}

### Response:
{response}
```

:::

:::{tab-item} Example

```bash
### Instruction
When did Virgin Australia start operating?

### Context
Virgin Australia, the trading name of Virgin Australia Airlines Pty Ltd, is an Australian-based airline. It is the largest airline by fleet size to use the Virgin brand. It commenced services on 31 August 2000 as Virgin Blue, with two aircraft on a single route. It suddenly found itself as a major airline in Australia's domestic market after the collapse of Ansett Australia in September 2001. The airline has since grown to directly serve 32 cities in Australia, from hubs in Brisbane, Melbourne and Sydney.

### Response:
Virgin Australia commenced services on 31 August 2000 as Virgin Blue, with two aircraft on a single route.
```

:::

::::

Ultimately, the choice between these two approaches depends on the specific requirements of the application and the desired level of control over the model's output. By employing the appropriate fine-tuning strategy, we can enhance the model's performance and make it more suitable for a wide range of applications and use cases.

### Training

There are many good libraries to help with this step, however, we are a fan of the [Transformer Reinforcement Learning (TRL)](https://huggingface.co/docs/trl) package, and the no-code [Hugging Face AutoTrain](https://huggingface.co/spaces/autotrain-projects/autotrain-advanced) for fine-tuning. In both cases, we need a backbone model, obtained from the [pre-training step](#pre-training) and for example purposes we will use our [curated Dolly dataset](https://huggingface.co/datasets/argilla/databricks-dolly-15k-curated-en).

```{note}
This dataset only contains a single annotator response per record. We gave some sugggestions on dealing with [responses from multiple annotators](/guides/llms/practical_guides/collect_responses).
```

```python
import argilla as rg
from datasets import Dataset

feedback_dataset = rg.FeedbackDataset.from_huggingface("argilla/databricks-dolly-15k-curated-en")
```

We can specify the training task that we're aiming to do, which is supervised fine-tuning (SFT). To do so, a formatting function must be provided.

```python
from argilla.feedback import TrainingTask
from typing import Dict, Any

template = """\
### Instruction: {instruction}\n
### Context: {context}\n
### Response: {response}"""

def formatting_func(sample: Dict[str, Any]) -> str:
    # What `sample` looks like depends a lot on your FeedbackDataset fields and questions
    return template.format(
        instruction=sample["new-instruction"][0]["value"],
        context=sample["new-context"][0]["value"],
        response=sample["new-response"][0]["value"],
    )

task = TrainingTask.for_supervised_fine_tuning(formatting_func=formatting_func)
```

You can observe the resulting dataset by calling `FeedbackDataset.prepare_for_training`. We can use `"trl"` as the framework for example:
```python
dataset = feedback_dataset.prepare_for_training(
    framework="trl",
    task=task
)
"""
>>> dataset
Dataset({
    features: ['id', 'text'],
    num_rows: 15015
})
>>> dataset[0]["text"]
### Instruction: When did Virgin Australia start operating?

### Context: Virgin Australia, the trading name of Virgin Australia Airlines Pty Ltd, is an Australian-based airline. It is the largest airline by fleet size to use the Virgin brand. It commenced services on 31 August 2000 as Virgin Blue, with two aircraft on a single route. It suddenly found itself as a major airline in Australia's domestic market after the collapse of Ansett Australia in September 2001. The airline has since grown to directly serve 32 cities in Australia, from hubs in Brisbane, Melbourne and Sydney.

### Response: Virgin Australia commenced services on 31 August 2000 as Virgin Blue, with two aircraft on a single route.
"""
```

#### TRL

The [Transformer Reinforcement Learning (TRL)](https://huggingface.co/docs/trl) package provides a flexible and customizable framework for fine-tuning models. It allows users to have fine-grained control over the training process, enabling them to define their functions and to further specify the desired behavior of the model. This approach requires a deeper understanding of reinforcement learning concepts and techniques, as well as more careful experimentation. It is best suited for users who have experience in reinforcement learning and want fine-grained control over the training process. Additionally, it directly integrates with [Parameter-Efficient Fine-Tuning](https://huggingface.co/docs/peft/index) (PEFT) decreasing the computational complexity of this step of training an LLM.

```python
from argilla.feedback import ArgillaTrainer

trainer = ArgillaTrainer(
    dataset=feedback_dataset,
    task=task,
    framework="trl",
    fetch_records=False,
    train_size=0.8,
    model="gpt2",
)
# e.g. using LoRA:
# from peft import LoraConfig
# trainer.update_config(peft_config=LoraConfig())
trainer.train(output_dir="sft_model")
```

Let's observe if it worked to train the model to respond within our template. We'll create a quick helper method for this.
```python
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
```
Let's first apply it to the non-finetuned GPT2 model:
```python
>>> generate("gpt2", "Is a toad a frog?")
### Instruction: Is a toad a frog?

### Context:

### Response:

###

###

###

###

###

###

###

###

###

###
>>> generate("gpt2", "Are dogs brown?")
### Instruction: Are dogs brown?

### Context:

### Response:

### Response:

### Response:

### Response:

### Response:

### Response:

```
And on our finetuned model:
```python
>>> generate("sft_model", "Is a toad a frog?")
### Instruction: Is a toad a frog?

### Context:

### Response: A frog is a small, round, black-eyed, frog with a long, black-winged head. It is a member of the family Pter
>>> generate("sft_model", "Are dogs brown?")
### Instruction: Are dogs brown?

### Context:

### Response: Dogs are brown. They are not brown. They are not brown. They are not brown. They are not brown. They are not brown. They are not
```
Much better! This model follows the template like we want.


####  TRLX

The other package is [Transformer Reinforcement Learning X (TRLX)](https://github.com/CarperAI/trlx), which has been heavily inspired by TRL but with an increased focus on incorporating Human Feedback into the training loop. However, out of the box, it also provides intuitive support for supervised `prompt-completion` fine-tuning using a relatively simple SDK, that takes tuples as `(prompt, completion)`. Take a look at the [RLHF section](#rlhf) for the other more feedback-oriented use cases of this library.

```python
import trlx

# Let's create a Dataset for convenience
data = {"instruction": [], "context": [], "response": []}
for entry in feedback_dataset:
    if entry.responses:
        res = entry.responses[0].values
        data["instruction"].append(res["new-instruction"].value)
        data["context"].append(res["new-context"].value)
        data["response"].append(res["new-response"].value)
dataset = Dataset.from_dict(data)

samples = [
    [
        f"### Instruction: {entry['instruction']} ### Context: {entry['context']}",
        f"### Response: {entry['response']}"
    ] for entry in dataset
]

trainer = trlx.train('gpt2', samples=samples)
```

#### AutoTrain

AutoTrain offers an option for users who prefer a simpler and more automated approach. It offers a no-code solution for fine-tuning models wrapped and enabled by a nice [streamlit UI](https://huggingface.co/spaces/autotrain-projects/autotrain-advanced), or by a low-code option with the [AutoTrain Advanced package](https://github.com/huggingface/autotrain-advanced). This tool leverages techniques to automatically optimize the model's performance without requiring users to have extensive knowledge of reinforcement learning or coding skills. It streamlines the fine-tuning process by automatically adjusting the model's parameters and optimizing its performance based on user-provided feedback.

First, export the data into CSV or any other supported format.

```python
dataset.to_csv("databricks-dolly-15k-curated-en.csv", index=False)
```

Then, go to the AutoTrain UI for training.

<iframe width="100%" height="600" src="https://www.youtube.com/embed/T_Lq8Zq-pwQ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

## RLHF

The last part of the fine-tuning process is the part that contains doing Reinforcement Learning with Human Feedback (RLHF). This is generally done by creating a reward model (RM) to rate responses in alignment with human preferences and afterward using this reward model to fine-tune the LLM with the associated scores.

```{note}
First, create a reward model or heuristic. Second, use this as automated procedure during reinforcment learning to align with human preferences.
```

### Data

The data required for these steps need to be used as comparison data to showcase the preference for the generated prompts. Like before, we will use our [curated Dolly dataset](https://huggingface.co/datasets/argilla/databricks-dolly-15k-curated-en), where we assumed that updated responses get preference over the older ones.

```python
import argilla as rg

feedback_dataset = rg.FeedbackDataset.from_huggingface("argilla/databricks-dolly-15k-curated-en")
```

### Training

Fine-tuning using a Reward Model can be done in different ways. We can either get the annotator to rate output completely manually, we can use a simple heuristic or we can use a stochastic preference model. Both TRL and TRLX provide decent options for incorporating rewards. The [DeepSpeed library of Microsoft](https://github.com/microsoft/DeepSpeed/tree/master/blogs/deepspeed-chat) is a worthy mention too but will not be covered in our docs.

#### TRL

[TRL](https://huggingface.co/docs/trl) has a direct reward modeling integration via the `RewardTrainer` class. This trains a classifier to mimic the human evaluation of generated texts. Afterward, we can use the `PPOTrainer` class for the reinforcement learning step in combination with the trained `RewardTrainer`. Conveniently, both of these are fully integrated into the `ArgillaTrainer`, allowing you to easily carry out RLHF.

::::{tab-set}

:::{tab-item} Reward modeling
[TRL](https://huggingface.co/docs/trl) implements reward modeling, which can be used via the `ArgillaTrainer` class. First of all, we must set up a formatting function that returns a `chosen-rejected` tuple. To determine which response from the FeedbackDataset is superior, we can use the user annotations.

```{note}
The formatting function can also return `None` or a list of tuples. The may be used if the annotations indicate that the text is low quality or harmful, and the latter could be used if multiple annotators provide additional written responses, resulting in multiple good `chosen-rejected` pairs.
```

What the parameter to `formatting_func` looks like depends a lot on your FeedbackDataset fields and questions.
However, fields (i.e. the left side of the Argilla annotation view) are provided as their values, e.g.
```python
>>> sample
{
    ...
    'original-response': 'Virgin Australia commenced services on 31 August 2000 '
                         'as Virgin Blue, with two aircraft on a single route.',
    ...
}
```
And all questions (i.e. the right side of the Argilla annotation view) are provided like so:
```python
>>> sample
{
    ...
    'new-response': [{'status': 'submitted',
                      'value': 'Virgin Australia commenced services on 31 August '
                               '2000 as Virgin Blue, with two aircraft on a '
                               'single route.',
                      'user-id': ...}],
    'new-response-suggestion': None,
    'new-response-suggestion-metadata': {'agent': None,
                                         'score': None,
                                         'type': None},
    ...
}
```

```python
from typing import Any, Dict, Iterator, Tuple
from argilla.feedback import TrainingTask

template = """\
### Instruction: {instruction}\n
### Context: {context}\n
### Response: {response}"""

def formatting_func(sample: Dict[str, Any]) -> Iterator[Tuple[str, str]]:
    # Our annotators were asked to provide new responses, which we assume are better than the originals
    og_instruction = sample["original-instruction"]
    og_context = sample["original-context"]
    og_response = sample["original-response"]
    rejected = template.format(instruction=og_instruction, context=og_context, response=og_response)

    for instruction, context, response in zip(sample["new-instruction"], sample["new-context"], sample["new-response"]):
        if response["status"] == "submitted":
            chosen = template.format(
                instruction=instruction["value"],
                context=context["value"],
                response=response["value"],
            )
            if chosen != rejected:
                yield chosen, rejected

task = TrainingTask.for_reward_modelling(formatting_func=formatting_func)
```
You can observe the dataset created using this task by using `FeedbackDataset.prepare_for_training`, for example using the "trl" framework:
```python
dataset = feedback_dataset.prepare_for_training(framework="trl", task=task)
"""
>>> dataset
Dataset({
    features: ['chosen', 'rejected'],
    num_rows: 2872
})
>>> dataset[2772]
{
    'chosen': '### Instruction: Answer based on the text: Is Leucascidae a sponge\n\n'
    '### Context: Leucascidae is a family of calcareous sponges in the order Clathrinida.\n\n'
    '### Response: Yes',
    'rejected': '### Instruction: Is Leucascidae a sponge\n\n'
    '### Context: Leucascidae is a family of calcareous sponges in the order Clathrinida.[1]\n\n'
    '### Response: Leucascidae is a family of calcareous sponges in the order Clathrinida.'}
"""
```
Looks great!

Now let's use the `ArgillaTrainer` to train a reward model with this task.
```python
from argilla.feedback import ArgillaTrainer

trainer = ArgillaTrainer(
    dataset=feedback_dataset,
    task=task,
    framework="trl",
    model="distilroberta-base",
)
trainer.train(output_dir="reward_model")
```

Let's try out the trained model in practice.
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model = AutoModelForSequenceClassification.from_pretrained("reward_model")
tokenizer = AutoTokenizer.from_pretrained("reward_model")

def get_score(model, tokenizer, text):
    # Tokenize the input sequences
    inputs = tokenizer(text, truncation=True, padding="max_length", max_length=512, return_tensors="pt")

    # Perform forward pass
    with torch.no_grad():
        outputs = model(**inputs)

    # Extract the logits
    return outputs.logits[0, 0].item()

# Example usage
prompt = "Is a toad a frog?"
context = "Both frogs and toads are amphibians in the order Anura, which means \"without a tail.\" Toads are a sub-classification of frogs, meaning that all toads are frogs, but not all frogs are toads."
good_response = "Yes"
bad_response = "Both frogs and toads are amphibians in the order Anura, which means \"without a tail.\""
example_good = template.format(instruction=prompt, context=context, response=good_response)
example_bad = template.format(instruction=prompt, context=context, response=bad_response)

score = get_score(model, tokenizer, example_good)
print(score)
# >> 5.478324890136719

score = get_score(model, tokenizer, example_bad)
print(score)
# >> 2.2948970794677734
```
As expected, the good response has a higher score than the worse response.

:::

:::{tab-item} Proximal Policy Optimization
The [TRL](https://huggingface.co/docs/trl) library also implements the last step of RLHF: Proximal Policy Optimization (PPO). It requires prompts, which are then fed through the model being finetuned. Its results are passed through a reward model. Lastly, the prompts, responses and rewards are used to update the model through reinforcement learning.

This tutorial uses the reward model trained in the last phase, but you can also use our [roberta-base-reward-model-falcon-dolly reward model](https://huggingface.co/argilla/roberta-base-reward-model-falcon-dolly).

As usual, we start with a task with a formatting function. For PPO, the formatting function only returns prompts.
```python
from argilla.feedback import TrainingTask
from typing import Dict, Any, Iterator

def formatting_func(sample: Dict[str, Any]) -> Iterator[str]:
    for instruction, context in zip(sample["new-instruction"], sample["new-context"]):
        if instruction["status"] == "submitted":
            yield template.format(
                instruction=instruction["value"],
                context=context["value"][:500],
                response=""
            ).strip()

task = TrainingTask.for_proximal_policy_optimization(formatting_func=formatting_func)
```

Like before, we can observe the resulting dataset:
```python
dataset = feedback_dataset.prepare_for_training(framework="trl", task=task)
"""
>>> dataset
Dataset({
    features: ['id', 'query'],
    num_rows: 15015
})
>>> dataset[922]
{'id': 922, 'query': '### Instruction: Is beauty objective or subjective?\n\n### Context: \n\n### Response:'}
"""
```

Instead of using this dataset, we'll use the task directly with our `FeedbackDataset` in the `ArgillaTrainer`. PPO requires us to specify the `reward_model`, and allows us to specify some other useful values as well:
* `reward_model`: A sentiment analysis pipeline with the reward model. This produces a reward for a prompt + response.
* `length_sampler_kwargs`: A dictionary with `min_value` and `max_value` keys, indicating the lower and upper bound on the number of tokens the finetuning model should generate while finetuning.
* `generation_kwargs`: The keyword arguments passed to the `generate` method of the finetuning model.
* `config`: A `trl.PPOConfig` instance with many useful parameters such as `learning_rate` and `batch_size`.

```python
from argilla.feedback import ArgillaTrainer
from transformers import pipeline
from trl import PPOConfig

trainer = ArgillaTrainer(
    dataset=feedback_dataset,
    task=task,
    framework="trl",
    model="gpt2",
)
reward_model = pipeline("sentiment-analysis", model="reward_model")
trainer.update_config(
    reward_model=reward_model,
    length_sampler_kwargs={"min_value": 32, "max_value": 256},
    generation_kwargs={
        "min_length": -1,
        "top_k": 0.0,
        "top_p": 1.0,
        "do_sample": True,
    },
    config=PPOConfig(batch_size=16)
)
trainer.train(output_dir="ppo_model")
```

After training, we can load this model and generate with it!
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("ppo_model")
tokenizer = AutoTokenizer.from_pretrained("ppo_model")
tokenizer.pad_token = tokenizer.eos_token

inputs = template.format(
    instruction="Is a toad a frog?",
    context="Both frogs and toads are amphibians in the order Anura, which means \"without a tail.\" Toads are a sub-classification of frogs, meaning that all toads are frogs, but not all frogs are toads.",
    response=""
).strip()
encoding = tokenizer([inputs], return_tensors="pt")
outputs = model.generate(**encoding, max_new_tokens=30)
output_text = tokenizer.decode(outputs[0])
print(output_text)
```

:::

::::

#### TRLX

[TRLX](https://github.com/CarperAI/trlx) gives the option to use a `reward function` or a `reward-labeled` dataset in combination with Proximal Policy Optimization (PPO) for the reinforcement learning step, which can be used by defining a PPO policy configuration. During this step, we infer rewards to mimic the human evaluation of generated texts. Additionally, [Hugging Face Accelerate](https://huggingface.co/docs/accelerate/index) can be used to speed up training or [Ray Tune](https://docs.ray.io/en/latest/tune/index.html) to optimize hyperparameter tuning.

```python
from trlx.data.default_configs import default_ppo_config

config = default_ppo_config()
config.model.model_path = 'gpt2'
config.train.batch_size = 16
```

::::{tab-set}

:::{tab-item} reward function

The [TRLX](https://github.com/CarperAI/trlx) `reward_fn` is quite flexible in its set up, however, most commonly you would expect to use a stochastic classification model obtained in a similar manner as the `RewardTrainer` defined above. For demo purposes, we provide an out-of-the-box [roberta-base-reward-model-falcon-dolly reward model](https://huggingface.co/argilla/roberta-base-reward-model-falcon-dolly).

```python
from transformers import pipeline
import trlx

dataset = ...
config = ...

classifier = pipeline("argilla/roberta-base-reward-model-falcon-dolly")

def my_reward_function(entry):
    return classifier(entry)[0].get("score")

trainer = trlx.train(
    config=config,
    reward_fn=lambda samples, **kwargs: [my_reward_function(sample) for sample in samples]
)
```

:::

:::{tab-item} reward-labeled dataset

In this case, TRLX relies on reward-labeled data to infer the alignment with human preference. This is a good approach but it is not recommended to only collect these labels via human feedback because this is likely too costly to scale. Therefore, we recommend using an automated reward function or creating a reward-labeled dataset using our [roberta-base-reward-model-falcon-dolly model](https://huggingface.co/argilla/roberta-base-reward-model-falcon-dolly). For demo purposes, we now infer the rewards from the corrected response, but we can also set up [specific ranking](../conceptual_guides/rm.html) using the Argilla UI.

```python
import trlx

dataset = ...
config = ...

samples, rewards = [], []
for entry in dataset:
    samples.append(entry["poorer_response"])
    rewards.append(1)
    samples.append(entry["better_response"])
    rewards.append(2)

trainer = trlx.train(config=config, samples=samples, rewards=rewards)
```

:::

::::

## Pre-training

When talking about pre-training, we generally talk about a simple `prompt-completion` task, where we need the model to pick up on basic statistics of the language it is learning. Given that you are familiar with Spanish cuisine and the prompt sentence, `The base ingredient of paella is ___`, you know that the word in the `___` is much more likely to be `rice` than `apples`.  So, you are basically training a causal language model or text generation model.

```{note}
This is an unsupervised approach hence we only infer training data from a basic sentence like `The base ingredient of paella is rice.` by starting with the word `The`, and from there unwrapping the sentence step by step.
```

### Data

Many training datasets for this task can be found online (e.g., [Hugging Face](https://huggingface.co/datasets?task_categories=task_categories:text-generation&sort=downloads)). You can either upload this in the right Argilla format but it might be needed to collect and fine-tune additional data with Argilla. So we, therefore, provide a basic setup underneath which should help you to start gathering or preparing pre-training data.

```{note}
When it comes to pre-training an LLM, we generally do not need data of highest quality, but it is always smart to use domain-specfic data and to avoid data that might lead to undecired effect like hallucination and bias.
```

First, create a `FeedbackDataset` with records.

```python
import argilla as rg

# create promp-completion dataset
dataset = rg.FeedbackDataset(
    guidelines="Please, complete the following prompt fields with a brief text answer.",
    fields=[
        rg.TextField(name="prompt"),
    ],
    questions=[
        rg.TextQuestion(name="completion", title="Add a brief text answer."),
    ]
)

# create a Feedback Records
record = rg.FeedbackRecord(
    fields={
        "prompt": "The base ingredient of paella is rice."
    }
)

dataset.add_records([record])
```

Then push it to Argilla via `push_to_argilla`.

::::{tab-set}

:::{tab-item} Argilla 1.14.0 or higher
```python
remote_dataset = dataset.push_to_argilla(name="pre-training")
```
:::

:::{tab-item} Lower than Argilla 1.14.0
```python
dataset.push_to_argilla(name="pre-training")
```
:::
::::

And, finally, load the `FeedbackDataset` from Argilla.

```python
import argilla as rg
from datasets import Dataset

dataset = rg.FeedbackDataset.from_argilla("pre-training")
prompts = {"prompt": [record.fields.get("prompt") for record in dataset.records]}
dataset = Dataset.from_dict(prompts)
dataset
# Dataset({
#     features: ['prompt'],
#     num_rows: 1
# })
```

### Training

There are many ways and great packages to deal with this `pre-training` phase, but generally, NLP training frameworks like [KerasNLP](https://keras.io/keras_nlp/) and [Hugging Face](https://huggingface.co/) offer great out-of-the-box methods for training a causal language model. In our guide, we will refer to the great docs off using Hugging Face `transformers` and `datasets` library and prepare our training data in the format they require for [training a causal language model](https://huggingface.co/learn/nlp-course/chapter7/6#training-a-causal-language-model-from-scratch).
