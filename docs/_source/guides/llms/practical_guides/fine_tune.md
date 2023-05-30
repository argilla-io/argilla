# Fine-tune an LLM

After [collecting the responses](/guides/llms/practical_guides/collect_responses) from our `FeedbackDataset` we can start fine-tuning our LLM. Due to the customizability of the task, this might require setting up a custom post-processing workflow but we will provide some good toy examples for the [classic LLM approaches](/guides/llms/conceptual_guides/rlhf): pre-training, supervised fine-tuning, reward modeling, and reinforcement learning.

## Supervised finetuning

The goal of Supervised Fine Tuning (SFT) is to optimize this pre-trained model to generate the responses that users are looking for. After pre-training a causal language model, it can generate feasible human text, but it will not be able to have proper `answers` to `question` phrases posed by the user in a conversational or instruction setting. Therefore, we need to collect and curate data tailored to this use case to teach the model to mimic this data. We have a section in our docs about [collecting data for this task](/guides/llms/conceptual_guides/sft.html) and there are many good [pre-trained causal language models](https://huggingface.co/models?pipeline_tag=text-generation&sort=downloads) available on Hugging Face.

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

There are many good libraries to help with this step, however, we are a fan of the Transformer Reinforcement Learning ([TRL](https://huggingface.co/docs/trl)) package and the no-code [Hugging Face AutoTrain](https://huggingface.co/spaces/autotrain-projects/autotrain-advanced) for fine-tuning. In both cases, we need a backbone model, obtained from the [pre-training step](#pre-training) and for example purposes we will use our [curated Dolly dataset](https://huggingface.co/datasets/argilla/databricks-dolly-15k-curated-en).

```python
import argilla as rg
from datasets import Dataset


feedback_dataset = rg.FeedbackDataset.from_huggingface("argilla/databricks-dolly-15k-curated-en")

data = {"instruction": [], "context": [], "response": []}
for entry in feedback_dataset:
    if entry.get("responses"):
        res = entry["responses"][0]["values"]
        data["instruction"].append(res["new-instruction"]["value"])
        data["context"].append(res["new-context"]["value"])
        data["response"].append(res["new-response"]["value"])

dataset = Dataset.from_dict(data)
```

```{note}
This dataset only contains a single annotator response per record. We gave some sugggestions on dealing with [responses from multiple annotators](/guides/llms/practical_guides/collect_responses).
```

####  TRL

The manual TRL package provides a flexible and customizable framework for fine-tuning models. It allows users to have fine-grained control over the training process, enabling them to define their functions and to further specify the desired behavior of the model. This approach requires a deeper understanding of reinforcement learning concepts and techniques, as well as more careful experimentation. It is best suited for users who have experience in reinforcement learning and want fine-grained control over the training process. Additionally, it directly integrates with [Performance Efficient Fine Tuning](https://huggingface.co/docs/peft/index) (PEFT) decreasing the computational complexity of this step of training an LLM.

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
        f"### Resposne: {example['response']}"
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

#### AutoTrain

AutoTrain offers an option for users who prefer a simpler and more automated approach. It offers a no-code solution for fine-tuning models wrapped and enabled by a nice [streamlit UI](https://huggingface.co/spaces/autotrain-projects/autotrain-advanced) or a low-code option with the [AutoTrain Advanced package](https://github.com/huggingface/autotrain-advanced). This option leverages techniques to automatically optimize the model's performance without requiring users to have extensive knowledge of reinforcement learning or coding skills. It streamlines the fine-tuning process by automatically adjusting the model's parameters and optimizing its performance based on user-provided feedback.

First, export the data.
```python
dataset = ...

dataset.to_csv("databricks-dolly-15k-curated-en.csv", index=False)
```
Second, start the UI for training.
<iframe width="100%" height="600" src="https://youtu.be/T_Lq8Zq-pwQ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

## RLHF

The last part of the fine-tuning process is the part that contains doing Reinforcement Learning with Human Feedback. This is generally done by training a reward model (RM) to rate responses in alignment with human preferences and afterward using this reward model to fine-tune the LLM with high-scoring responses.

### Data

The data required for these steps need to be used as comparison data to showcase the preference for the generated prompts. Therefore, we need to have a classification dataset with a `better_response` and a `poorer_responses`. These are then used to train a preference classifier. There are several public datasets [available](https://huggingface.co/datasets?search=rlhf) but a good baseline can be found in the one that is the one offered by [Anthropic](https://huggingface.co/datasets/Anthropic/hh-rlhf). We will however showcase how to use our [curated Dolly dataset](https://huggingface.co/datasets/argilla/databricks-dolly-15k-curated-en), where we assumed that updated responses get preference over the older ones.

```python
import argilla as rg
from datasets import Dataset


feedback_dataset = rg.FeedbackDataset.from_huggingface("argilla/databricks-dolly-15k-curated-en")

data = {"instruction": [], "context": [], "poorer_responses": [], "better_response": []}
for entry in feedback_dataset:
    if entry.get("responses"):
        res = entry["responses"][0]["values"]
        if res["new-response"]["value"] != res["original-response"]["value"]:
            data["instruction"].append(res["new-instruction"]["value"])
            data["context"].append(res["new-context"]["value"])
            data["poorer_responses"].append(res["original-response"]["value"])
            data["better_response"].append(res["new-response"]["value"])

dataset = Dataset.from_dict(data)
```

### Training
#### Reward Model



#### Fine-tuning using Reward Model

## Pre-training

When talking about pre-training, we generally talk about a simple `prompt-completion` task, where we need the model to pick up on basic statistics of the language it is learning. Given that you are familiar with Spanish cuisine and the prompt sentence, `The base ingredient of paella is ___`, you know that the word in the `___` is much more likely to be `rice` than `apples`.  So, you are basically training a causal language model or text generation model.

```{note}
This is an unsupervised approach hence we only infer training data from a basic sentence like `The base ingredient of paella is rice.` by starting with the word `The`, and from there unwrapping the sentence step by step.
```

### Data

Many training datasets for this task can be found online (e.g., [Hugging Face](https://huggingface.co/datasets?task_categories=task_categories:text-generation&sort=downloads)). You can either upload this in the right Argilla format but it might be needed to collect and fine-tune additional data with Argilla. So we, therefore, provide a basic setup underneath which should help you to start gathering or preparing pre-training data.

```python
import argilla as rg

# create promp-completion dataset
dataset = rg.FeedbackDataset(
    guidelines="Please, complete the following prompt fields with a brief text answer.",
    fields=[
        rg.TextField(name="content"),
    ],
)

# create a Feedback Records
record = [
	rg.FeedbackRecord(
		fields={
			"content": "The base ingredient of paella is rice.",
        }
	)
]
rg.add_records(record)
dataset.push_to_argilla(name="pre-training")
```

```{note}
When it comes to pre-training an LLM, we generally do not need data of highest quality, but it is always smart to use domain-specfic data and to avoid data that might lead to undecired effect like hallucination and bias.
```

### Training

There are many ways and great packages to deal with this `pre-training` phase, but generally, NLP training frameworks like [KerasNLP](https://keras.io/keras_nlp/) and [Hugging Face](https://huggingface.co/) offer great out-of-the-box methods for training a causal language model. In our guide, we will be using Hugging Face `transformers` and `datasets` library and prepare our training data in the format they require for [training a causal language model](https://huggingface.co/learn/nlp-course/chapter7/6#training-a-causal-language-model-from-scratch).

```python
import argilla as rg
from datasets import Dataset

feedback = rg.FeedbackDataset.from_argilla("pre-training")
content = {"content": [rec.get("fields").get("content") for rec in feedback]}
dataset = Dataset.from_dict(content)
dataset
# Dataset({
#     features: ['content'],
#     num_rows: 1
# })
```
