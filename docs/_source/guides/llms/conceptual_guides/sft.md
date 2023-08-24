# Collecting demonstration data

This guide explains how to implement workflows for collecting demonstration data. As covered in the ["Data Collection for Large Language Models" guide](rlhf.md), the importance of demonstration data - **prompts and demonstrations** - is paramount for improving LLMs. This data aids in supervised fine-tuning, also known as instruction-tuning or behavior cloning, where models learn to respond based on human examples. Despite being seen as labor-intensive, recent research like the LIMA work indicates that even a small set of 1,000 diverse, high-quality examples can efficiently train a model. Argilla Feedback was developed to **simplify this process, distributing it among multiple labelers in your organization**.

:::{tip}
You can add unlimited users to Argilla datasets so it can be seamlessly used to **distribute the workload among hundreds of labelers or experts within your organization**. Similar efforts include Dolly from Databricks or OpenAssistant. If you’d like help setting up such an effort, [reach out to us and we’ll gladly help out](https://tally.so/r/mBzNde).
:::

The following figure illustrates the steps to collect feedback from a team of labelers and perform supervised fine-tuning. The steps are: **configure the dataset**, **add records**, **labelers write demonstrations**, **prepare the dataset**, and **fine-tune the SFT model**.

<img src="../../../_static/images/llms/sft.svg" alt="Demonstration collection for SFT" style="display:block;margin-left:auto;margin-right:auto;">

:::{note}
The following sections give a detailed, conceptual description of the above steps. For a hands-on practical introduction, go directly to the How-to Guides or Examples section.
:::

## Configure the dataset

The aim of this phase is to configure a dataset for gathering human demonstrations for each `prompt`.

First, we need to configure a **dataset**. Argilla datasets allow you to mix different **questions** for labelers to answer. In this case, we want to collect **demonstrations** from our labelers. We’ll just need to define a **text question**. Datasets are configured using the Argilla Python SDK. This is how you can define this field:

```python
import argilla as rg

questions =[
    rg.TextQuestion(
        name="demonstration",
        title="Please write a harmless and helpful response for the prompt:",
        required=True
    )
]
```

Argilla Datasets are composed of **records**. A **record** is a data point that can be labeled by one or more labelers. A record consists of one or more **fields**. These fields and the order in which they are presented to labelers are fully configurable. In this case, we want to show labelers a prompt. We’ll just need to define a *text field*. This is how you can define this field:

```python
fields = [
    rg.TextField(name="prompt", required=True)
]
```

To configure the dataset, the final step is to define the **guidelines** for labelers. These guidelines help labelers understand and answer the questions consistently. This is how you can configure the dataset, including the guidelines:

```python
dataset = rg.FeedbackDataset(
	guidelines="Please, read the prompt carefully and...",
	questions=questions,
	fields=fields
)
```

## Add records

The aim of this phase is to create records with `prompts` to be pushed into Argilla for collecting human `completions`.

Once you have configured the dataset, you need to add records and publish them for labelers. In this case, the records will contain a single field, the **prompt**. This **prompt** will be shown to labelers in the UI and we will ask them to provide a **completion**. The most important questions at this step are: **where to get the prompts from** and **how to select them** in order to maximize the quality of the resulting LLM.

:::{tip}
Important features for the resulting dataset include diversity, consistent completion style, and quality. These features must be considered when designing the data selection and collection processes.
:::

For collecting **prompts** or instructions, there are at least the following options:

### Use an existing internal database of prompts or user queries related to your use case
If your goal is to fine-tune an LLM for your use case, this is the best option. As shown by the recent “LIMA: Less is More for Alignment” paper, you can get good results by collecting a diverse, high-quality, consistent dataset of 1,000-5,000 examples. Previous research uses 13,000 to 20,000 examples.

:::{tip}
As the field is rapidly evolving and lacking consensus, we suggest beginning with a small dataset of the highest quality. Argilla Feedback is built for iteration. Starting small allows for faster iteration: training is cheaper and faster, and the length of the feedback loop is reduced.
:::

### Use an open dataset of prompts or user queries

If you don’t have an internal database for your use case, you can sample and select prompts from an open dataset. The steps here can include: (1) **finding an open dataset** that might contain prompts related to your use case, (2) performing** exploratory data** analysis and topic extraction** to understand the data, and (3) **filtering and selecting prompts** based on topic, quality, text descriptives, etc.

Some available datasets are [ShareGPT](https://huggingface.co/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered), [Open Assistant Conversation Dataset](https://huggingface.co/datasets/OpenAssistant/oasst1), or [Stack Exchange](https://huggingface.co/datasets/HuggingFaceH4/stack-exchange-preferences). Please be aware that some of these datasets might contain inappropriate, irrelevant, or bad-quality examples for your use case.

:::{note}
Open datasets might contain responses, so you might think about skipping the data collection process entirely. If you want to build a good quality instruction-following model for your use case, these datasets cover a wide range of topics, but the responses may not fit your use case's quality and style. Also, there are several models already trained with these datasets. If you think the quality and style of the data already fit your use case, we recommend running an evaluation campaign using one of the models with your own data.
:::

An alternative is to obtain a dataset of user queries in your domain and apply the same process of data analysis and sampling. A good strategy is to search for datasets of user intent or utterances. For example, if you plan to fine-tune an LLM for a customer service banking assistant, you might start with the [banking77](https://huggingface.co/datasets/banking77) dataset.

### Ask humans to write prompts or instructions

If none of the above is possible, a third option is to ask humans to write prompts for your use case. This option is expensive and has limitations. The main limitation is the risk of creating artificial prompts that won't match the diversity, topics, or writing style of end-users if the prompts are not written by them. Besides involving end-users in the process, this limitation might be overcome by defining clear guidelines and preparing a diverse set of topics. Such effort can be easily set up with Argilla Feedback by using **guidelines** and creating records with a **text field** indicating the labeler what to write the prompt about. By adding this field, you can control the diversity and desired distribution of prompt topics. This is how you can set up the field and the question using the Python SDK:

```python
# this will be populated from the list of writing topics you create
fields = [
    rg.TextField(name="writing-topic", required=True)
]

# we will ask the labeler to write a possible prompt or instruction
question = rg.TextQuestion(
	name="prompt",
	title="Imagine and write a possible instruction for the given topic:",
	required=True
)
```

Please note that you can also ask labelers to respond to the proposed instruction. This strategy may work depending on the project and resources available, but it can make labeling more complex and affect overall consistency.

:::{tip}
No matter the option you choose, for maximum quality, we recommend building a feedback workflow with Argilla where you ask labelers to rate the quality of prompts. You can use the aggregated ratings to select the highest-quality examples.
:::

Once you have the dataset with prompts ready, you just need to create the records, add them to the dataset, and push the dataset to Argilla to make it available for labelers (or yourself):

```python
from datasets import load_dataset

# This is only for demonstration and assumes you use a HF dataset
prompts = load_dataset('your_prompts_dataset', split=["train"])

records = [
	rg.FeedbackRecord(fields={"prompt": record["prompt"]})
	for record in dataset
]

dataset.add_records(records)
```

::::{tab-set}

:::{tab-item} Argilla 1.14.0 or higher
```python
# This publishes the dataset with its records to Argilla and returns the dataset in Argilla
remote_dataset = dataset.push_to_argilla(name="my-dataset", workspace="my-workspace")
```
:::

:::{tab-item} Lower than Argilla 1.14.0
```python
# This publishes the dataset with its records to Argilla and turns the dataset object into a dataset in Argilla
dataset.push_to_argilla(name="my-dataset", workspace="my-workspace")
```
:::
::::

## Labelers write completions
The aim of this phase is to provide human demonstrations for each `prompt` using Argilla UI.

Once you upload your dataset to Argilla, it becomes accessible via the Argilla UI. Argilla Feedback allows simultaneous feedback collection from multiple users, enhancing quality control. Each user with dataset access can give feedback.

However, when resources are scarce, workload distribution among various labelers is recommended. This strategy entails assigning each labeler a subset of records to label. This [how-to guide](../practical_guides/set_up_annotation_team.html) provides detailed instructions on setting up these workload distribution options effectively.

For a comprehensive understanding of the Argilla UI's main features, refer to this [how-to guide](../practical_guides/annotate_dataset.html).

## Prepare the dataset

The aim of this phase is to compile a dataset into `prompt` and `demonstration` pairs that will be used for supervised fine-tuning.

Once the dataset has been labeled, you can retrieve the responses using the Python SDK as follows:

```python
# Assume we distribute the workload in one dataset with several labelers
feedback = rg.FeedbackDataset.from_argilla(
	name="my-dataset",
	workspace="my-workspace"
)
```

Your work distribution strategy may require you to gather and consolidate responses from multiple datasets and workspaces. Let's consider a scenario where you've divided the task among four labelers. Here's how you can retrieve their responses:

```python
# Assume the workload has been divided across the following workspaces
user_workspaces = ["natalia", "amelie", "tom", "dani"]

# this will hold each user's subsets
feedback_datasets = []

for workspace in user_workspaces:
	feedback = rg.FeedbackDataset.from_argilla(
		name="my-dataset",
		workspace=workspace
	)
	feedback_datasets.append(feedback)
```

Every record in `feedback.records` contain a `responses` attribute, which holds any feedback provided for that record. Each response includes:

- `user_id`: The annotator's Argilla user ID.
- `values`: The feedback given by the annotator. It's formatted as a dictionary, with keys for each question and values holding the respective answers.
- `status`: The condition of the response - `submitted` or `discarded`. For our purposes, we focus on the `submitted` records.

For datasets without annotation overlap, meaning each record has a single response, post-processing is simple as there's no need to choose which annotations to keep. If overlaps exist, refer to [this guide](../practical_guides/collect_responses.html) for conflict resolution strategies.

Upon reconciling, we aim to have a list of records each with a `demonstration` answer, to be used for fine-tuning.

Additionally, records include a `fields` attribute, outlining all fields set during dataset creation. In this case, we have `prompt` to use as input for fine-tuning.

After gathering one `demonstration` per `prompt`, the last step is to prep your dataset for fine-tuning your base LLM. This preparation hinges on your selected fine-tuning framework. [This guide](../practical_guides/fine_tune.html) discusses the options and respective data preparation methods.
