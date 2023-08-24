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

data = {"instruction": [], "context": [], "response": []}
for entry in feedback_dataset:
    if entry.responses:
        res = entry.responses[0].values
        data["instruction"].append(res["new-instruction"].value)
        data["context"].append(res["new-context"].value)
        data["response"].append(res["new-response"].value)

dataset = Dataset.from_dict(data)
dataset
# Dataset({
#     features: ['instruction', 'context', 'response'],
#     num_rows: 15000
# })
```

####  TRL

The [Transformer Reinforcement Learning (TRL)](https://huggingface.co/docs/trl) package provides a flexible and customizable framework for fine-tuning models. It allows users to have fine-grained control over the training process, enabling them to define their functions and to further specify the desired behavior of the model. This approach requires a deeper understanding of reinforcement learning concepts and techniques, as well as more careful experimentation. It is best suited for users who have experience in reinforcement learning and want fine-grained control over the training process. Additionally, it directly integrates with [Performance Efficient Fine Tuning](https://huggingface.co/docs/peft/index) (PEFT) decreasing the computational complexity of this step of training an LLM.

```python
from transformers import AutoModelForCausalLM
from datasets import load_dataset
from trl import SFTTrainer

dataset = ...

model = AutoModelForCausalLM.from_pretrained("facebook/opt-350m")

def formatting_prompts_func(example):
    text = (
        f"### Instruction: {example['instruction']}\n" +
        f"### Context: {example['context']}\n" +
        f"### Response: {example['response']}"
    )
    return text

trainer = SFTTrainer(
    model,
    train_dataset=dataset,
    packing=True,
    formatting_func=formatting_prompts_func,
    # peft_config=LoraConfig() # from peft import LoraConfig
)

trainer.train()
```

####  TRLX

The other package is [Transformer Reinforcement Learning X (TRLX)](https://github.com/CarperAI/trlx), which has been heavily inspired by TRL but with an increased focus on incorporating Human Feedback into the training loop. However, out of the box, it also provides intuitive support for supervised `prompt-completion` fine-tuning using a relatively simple SDK, that takes tuples as `(prompt, completion)`. Take a look at the [RLHF section](#rlhf) for the other more feedback-oriented use cases of this library.

```python
import trlx

# dataset = ...

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
dataset = ...

dataset.to_csv("databricks-dolly-15k-curated-en.csv", index=False)
```

Then, go to the AutoTrain UI for training.

<iframe width="100%" height="600" src="https://www.youtube.com/embed/T_Lq8Zq-pwQ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

## RLHF

The last part of the fine-tuning process is the part that contains doing Reinforcement Learning with Human Feedback (RLHf). This is generally done by creating a reward model (RM) to rate responses in alignment with human preferences and afterward using this reward model to fine-tune the LLM with the associated scores.

```{note}
First, create a reward model or heuristic. Second, use this as automated procedure during reinforcment learning to align with human preferences.
```

### Data

The data required for these steps need to be used as comparison data to showcase the preference for the generated prompts. Therefore, we need to have a classification dataset with a `better_response` and a `poorer_responses`. These are then used to train a preference classifier. There are several public datasets [available](https://huggingface.co/datasets?search=rlhf) but a good baseline can be found in the one that is the one offered by [Anthropic](https://huggingface.co/datasets/Anthropic/hh-rlhf). We will however showcase how to use our [curated Dolly dataset](https://huggingface.co/datasets/argilla/databricks-dolly-15k-curated-en), where we assumed that updated responses get preference over the older ones.

```python
import argilla as rg
from datasets import Dataset

feedback_dataset = rg.FeedbackDataset.from_huggingface("argilla/databricks-dolly-15k-curated-en", split="train")

data = {"instruction": [], "context": [], "poorer_response": [], "better_response": []}
for entry in feedback_dataset:
    if entry.responses:
        res = entry.responses[0].values
        original_input = entry.fields["original-response"]
        if original_input != res["new-response"].value:
            data["instruction"].append(res["new-instruction"].value)
            data["context"].append(res["new-context"].value)
            data["poorer_response"].append(original_input)
            data["better_response"].append(res["new-response"].value)

dataset = Dataset.from_dict(data)
dataset
# Dataset({
#     features: ['instruction', 'context', 'poorer_response', 'better_response'],
#     num_rows: 475
# })
```

### Training

Fine-tuning using a Reward Model can be done in different ways. We can either get the annotator to rate output completely manually, we can use a simple heuristic or we can use a stochastic preference model. Both TRL and TRLX provide decent options for incorporating rewards. The [DeepSpeed library of Microsoft](https://github.com/microsoft/DeepSpeed/tree/master/blogs/deepspeed-chat) is a worthy mention too but will not be covered in our docs.

#### TRL

[TRL](https://huggingface.co/docs/trl) has a direct reward modeling integration via the `RewardTrainer` class. This trains a classifier to mimic the human evaluation of generated texts. Afterward, we can use the `PPOTrainer` class for the reinforcement learning step in combination with the trained `RewardTrainer`.

::::{tab-set}

:::{tab-item} RewardTrainer
[TRL](https://huggingface.co/docs/trl) has a direct reward modeling integration via the `RewardTrainer` class. This class functions similarly to the SFTTrainer and TransformersTrainer but requires `rejected-accepted` input pairs as training data. These are then used to fine-tune an `AutoModelForSequenceClassification` which we can use as a reward model during the reinforcement learning phase. The entries within the dataset should be `input_ids_chosen`, `attention_mask_chosen`, `input_ids_rejected` and `attention_mask_rejected` so we should first format them. The [roberta-base-reward-model-falcon-dolly reward model](https://huggingface.co/argilla/roberta-base-reward-model-falcon-dolly) was trained using the code below.

```python
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    TrainingArguments,
)
​
from trl import RewardTrainer
​
from datasets import load_dataset
​
dataset = load_dataset("argilla/dolly-curated-comparison-falcon-7b-instruct", split="train")
​
model_name = "distilroberta-base"
​
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=1)
tokenizer = AutoTokenizer.from_pretrained(model_name)
​
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
    model.config.pad_token_id = model.config.eos_token_id
​
def formatting_func(examples):
    kwargs = {"padding": "max_length", "truncation": True, "max_length": 512, "return_tensors": "pt"}
​
    # Assuming original human response is preferred to Falcon's
    chosen_response = examples["original_response"]
    rejected_response = examples["response-1"]
    prompt = examples["prompt"]
​
    tokens_chosen = tokenizer.encode_plus(prompt, chosen_response, **kwargs)
    tokens_rejected = tokenizer.encode_plus(prompt, rejected_response, **kwargs)
​
    return {
        "input_ids_chosen": tokens_chosen["input_ids"][0], "attention_mask_chosen": tokens_chosen["attention_mask"][0],
        "input_ids_rejected": tokens_rejected["input_ids"][0], "attention_mask_rejected": tokens_rejected["attention_mask"][0]
    }

formatted_dataset = dataset.map(formatting_func)
​
trainer = RewardTrainer(
    model=model,
    args=TrainingArguments("output_dir"),
    tokenizer=tokenizer,
    train_dataset=formatted_dataset
)
​
trainer.train()
```
:::

:::{tab-item} PPOTrainer
The [TRL](https://huggingface.co/docs/trl) `PPOTrainer` allows updating while plugging in any arbitrary model or heuristic to assign `rewards` to the generated output. In the example below, we use the  `reward_model` and `reward_tokenizer` to create a transformers text-classification pipeline. This pipeline is then used to create `rewards` which are then passed during the PPO `.step()` to include in the weigh optimization for the next batch. You can choose to use our [roberta-base-reward-model-falcon-dolly reward model](https://huggingface.co/argilla/roberta-base-reward-model-falcon-dolly).

```python
import torch
from transformers import AutoTokenizer, pipeline
from trl import AutoModelForCausalLMWithValueHead, PPOConfig, PPOTrainer
from trl.core import LengthSampler

reward_model = ... # "argilla/roberta-base-reward-model-falcon-dolly"
reward_tokenizer = ... # "argilla/roberta-base-reward-model-falcon-dolly"

config = PPOConfig(model_name="gpt2", batch_size=2)

model = AutoModelForCausalLMWithValueHead.from_pretrained(config.model_name)
ref_model = AutoModelForCausalLMWithValueHead.from_pretrained(config.model_name)
tokenizer = AutoTokenizer.from_pretrained(config.model_name)
tokenizer.pad_token = tokenizer.eos_token
reward_pipe = pipeline(model=reward_model, tokenizer=reward_tokenizer)

def formatting_func(examples):
    kwargs = {
        "padding": "max_length", "truncation": True,
        "max_length": 512, "return_tensors": "pt"
    }
    input_size = LengthSampler(min_value=2, max_value=8)
    input_text = examples["instruction"] + examples["context"] + examples["response"]
    examples["input_ids"] = tokenizer.encode(input_text, **kwargs)[0][: input_size()]
    examples["query"] = tokenizer.decode(examples["input_ids"][0])
    return examples

formatted_dataset = dataset.map(formatting_func, batched=False)
formatted_dataset.set_format(type="torch")

def collator(data):
    return dict((key, [d[key] for d in data]) for key in data[0])

ppo_trainer = PPOTrainer(config, model, ref_model, tokenizer, dataset=formatted_dataset, data_collator=collator)

output_min_length = 4
output_max_length = 16
output_length_sampler = LengthSampler(output_min_length, output_max_length)

generation_kwargs = {
    "min_length": -1,
    "top_k": 0.0,
    "top_p": 1.0,
    "do_sample": True,
    "pad_token_id": tokenizer.eos_token_id,
}

for epoch, batch in enumerate(ppo_trainer.dataloader):
    query_tensors = batch["input_ids"]

    #### Get response from gpt2
    response_tensors = []
    for query in query_tensors:
        gen_len = output_length_sampler()
        generation_kwargs["max_new_tokens"] = gen_len
        response = ppo_trainer.generate(query, **generation_kwargs)
        response_tensors.append(response.squeeze()[-gen_len:])
    batch["response"] = [tokenizer.decode(r.squeeze()) for r in response_tensors]

    #### Compute sentiment score
    texts = [q + r for q, r in zip(batch["query"], batch["response"])]
    pipe_outputs = reward_pipe(texts, return_all_scores=True)
    rewards = [torch.tensor(output[1]["score"]) for output in pipe_outputs]

    #### Run PPO step
    stats = ppo_trainer.step(query_tensors, response_tensors, rewards)
    ppo_trainer.log_stats(stats, batch, rewards)
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
