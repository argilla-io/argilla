# Collecting comparison data

This guide will help you set up workflows for **collecting comparison data to train a reward model**. As covered in the ["Data Collection for Large Language Models" guide](rlhf.md), RLHF involves training a reward model to rate responses in alignment with human preferences. Subsequently, the LLM is fine-tuned using Reinforcement Learning (RL) to generate high-scoring responses as per the reward model. While the reward model scores prompt-response pairs, comparison data is generally gathered differently. This typically involves **humans ranking several responses to a particular prompt from best to worst**.

The steps to implement the comparison data collection process with Argilla are: **create the dataset**, **add records**, **labelers rank responses**, **prepare the dataset**, and **train the reward model**.

<img src="/_static/images/llms/rm.svg" alt="Comparison collection for Reward Modeling" style="display:block;margin-left:auto;margin-right:auto;">

:::{note}
For a practical hands-on introduction, you may directly proceed to the How-to Guides or Examples section. This guide focuses on providing a detailed, conceptual description of the process.
:::

### Create the dataset

In this phase, you'll set up a dataset to gather ranked responses to each `prompt`.

First, let's configure a **dataset** using the Argilla Python SDK. This dataset will contain **questions** for labelers to answer. In this case, we want to collect ranked responses from our labelers. We’ll define a **RankingQuestion**:

```python
import argilla as rg

questions = [
    rg.RankingQuestion(
        name="response_ranking",
        title="Order the responses based on their accuracy and helpfulness:",
        required=True,
        values={"response-1": "Response 1", "response-2": "Response 2"} # or ["response-1", "response-2"]
    )
]
```

:::{hint}
If you only have 2 options, you can also do this with a `RatingQuestion`:

```python
import argilla as rg

questions = [
    rg.RatingQuestion(
        name="response_ranking",
        title="Select the most accurate and helpful response (1) or (2). If both are equal select (0):",
        required=True,
        values=[0, 1, 2]
    )
]
```
:::

The dataset consists of **records**. Each **record** is a data point that can be labeled by one or more labelers. A record has one or more **fields**. For this task, we need to present labelers with a prompt and two responses to rank. We’ll define a **text field**:

```python
fields = [
    rg.TextField(name="prompt", required=True),
    rg.TextField(name="response-1", required=True),
    rg.TextField(name="response-2", required=True)
]
```

Next, define **guidelines** for labelers. These instructions help labelers understand and answer the questions consistently:

```python
dataset = rg.FeedbackDataset(
    guidelines="Please, read the prompt carefully and...",
    questions=questions,
    fields=fields
)
```

### Add records

This phase aims to create records with a `prompt` and two generated `responses` to be pushed into Argilla for collecting human `rankings`.

Once you have configured the dataset, you need to add records and publish them for labelers. In this case, the records will contain three fields: the **prompt**, **response 1**, and **response 2**. The **prompt** and the two **responses** will be shown to labelers in the UI and we will ask them to rank the two responses. The most important questions at this step are: **how to generate the two responses** in order to maximize the quality and variety of the resulting LLM.

:::{tip}
Important features of the resulting dataset include diversity, consistent response style, and quality. These features must be considered when designing the data selection and collection processes.
:::

The responses can be generated using a pre-trained LLM, fine-tuned on a prior dataset. You can use different strategies to generate the responses, such as generating multiple responses and selecting two, or generating two responses with different parameters (e.g., temperature).

Assuming that you have a pre-trained LLM, here's how you can **generate the responses using the instruction-following model Falcon-7B-instruct**:

```python
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

# Load the model and tokenizer
model = AutoModelForCausalLM.from_pretrained("tiiuae/falcon-7b-instruct")
tokenizer = AutoTokenizer.from_pretrained("tiiuae/falcon-7b-instruct")

# Create a pipeline for text generation
gen_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# Load your dataset of prompts
prompts = load_dataset("your_prompts_dataset", split=["train"])

records = []
for record in prompts:
    prompt = record["prompt"]

    # Generate two responses in one call
    outputs = gen_pipeline(
        prompt,
        max_length=100,
        do_sample=True,
        top_k=10,
        num_return_sequences=2,
        eos_token_id=tokenizer.eos_token_id,
    )
    responses = [output["generated_text"] for output in outputs]

    record = rg.FeedbackRecord(fields={"prompt": prompt, "response 1": responses[0], "response 2": responses[1]})
    records.append(record)

# Add records to the dataset
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

The above code will generate two responses for each prompt and push these records to Argilla. Labelers will see these prompts and responses, and rank the responses according to the instructions provided in the dataset.

Here's an example of a record generated with the above code:

| Prompt | Response 1 | Response 2 |
|--------|------------|------------|
| Write a follow-up for a sales email | Dear [Customer Name],<br/><br/>Thank you for purchasing [Product Name] from us last week. We hope you have been enjoying using it!<br/><br/>If you have any questions or feedback about your purchase, please do not hesitate to let us know. We are always happy to help.<br/><br/>Best regards,<br/>[Sales Team] | Dear [Customer Name],<br/><br/>Thank you for your recent purchase [Product Name]. We hope you're enjoying your [Product Name] as much as we are here at [Company Name].<br/><br/>If you have any questions or feedback regarding your purchase, please don't hesitate to let us know. We"d love the chance to make your shopping experience even better.<br/><br/>Thank you again for your purchase,<br/>[Company Name] |

:::{note}
The ranking task can be challenging for labelers if the two responses are very similar. Consider adjusting the parameters of the generation process (e.g., the temperature) to produce more varied responses.
:::

:::{tip}
As the field is rapidly evolving and lacking consensus, we suggest beginning with a small dataset of the highest quality. Argilla Feedback is built for iteration. Starting small allows for faster iteration: training is cheaper and faster, and the length of the feedback loop is reduced.
:::

## Labelers rank responses

This phase aims to provide human rankings for pairs of responses to a given `prompt` using the Argilla UI.

Once you upload your dataset to Argilla, it becomes accessible via the Argilla UI. Argilla Feedback allows simultaneous feedback collection from multiple users, enhancing quality control. Each user with dataset access can give feedback.

However, when resources are limited, workload distribution among various labelers is recommended. This strategy entails assigning each labeler a subset of records to rank. This [how-to guide](/practical_guides/assign_records) provides detailed instructions on setting up these workload distribution options effectively.

For a comprehensive understanding of the Argilla UI's main features, refer to this [how-to guide](/practical_guides/annotate_dataset).

## Prepare the dataset

The goal of this phase is to organize a dataset into prompt, preferred response, and less preferred response triplets. This data structure will be used for training the reward model.

Once you've distributed the labeling tasks and collected the responses from labelers, these can be retrieved using the Python SDK as follows:

```python
# Assume we distribute the workload in one dataset across multiple labelers
feedback = rg.FeedbackDataset.from_argilla(
    name="my-dataset",
    workspace="my-workspace"
)
```

If your work distribution strategy requires gathering responses from multiple datasets and workspaces, you'll need to retrieve and consolidate responses from each source. For example, if the task was divided among four labelers, here's how you can retrieve their responses:

```python
# Assume the workload has been divided across the following workspaces
user_workspaces = ["natalia", "amelie", "tom", "dani"]

# This will hold each user's subsets
feedback_datasets = []

for workspace in user_workspaces:
    feedback = rg.FeedbackDataset.from_argilla(
        name="my-dataset",
        workspace=workspace
    )
    feedback_datasets.append(feedback)
```

Each record in `feedback.records` contain a `responses` attribute, which houses the feedback provided for that record. The structure of each response includes:

- `user_id`: The Argilla user ID of the labeler.
- `values`: The feedback provided by the labeler. This is formatted as a dictionary, with keys for each question and values holding the respective answers.
- `status`: The status of the response, which can be either submitted or discarded. For our purposes, we're only interested in the submitted responses.

For datasets where each record has a single response (no annotation overlap), post-processing is straightforward as there's no need to resolve conflicts between different annotations. However, if annotation overlaps exist, conflict resolution becomes necessary. For strategies on conflict resolution, refer to [this guide](/practical_guides/collect_responses.md#unifying-disagreements).

```{tip}
Sharing the comparison data collection among multiple labelers can be beneficial. Each labeler identifies their favored response for a specific prompt. By pooling these choices, we can derive a collective ranking for all responses.
````

In addition, each record contains a `fields` attribute, which includes all the fields set during dataset creation. In this case, prompt, response 1, and response 2 are inputs for the reward model, with preference rankings attached.

Upon resolving conflicts, the aim is to have a list of records each indicating a preference for one response over the other to a prompt. These will be used for training the reward model.

For demonstration purposes, here is a step-by-step code snippet to create a dataset of triplets `(prompt, preferred response, less preferred response)` from a single dataset without overlapping annotations:

```python
# Define an empty list to store the triplets
triplets = []

# Loop over all records in the dataset
for record in feedback.records:
    # Ensure that the record has responses
    if record.responses is None or len(record.responses) == 0:
        continue

    # Ensure the response has been submitted (not discarded)
    response = record.responses[0]

    if response.status == 'submitted':
        # Get the ranking value from the response for the preferred and least preferred
        # responses, assuming there are no ties
        preferred_rank = response.values["response_ranking"].value[0]["value"]
        least_preferred_rank = response.values["response_ranking"].value[1]["value"]

        # Construct the triplet and append to the list
        triplets.append({
            "prompt": record.fields["prompt"],
            "preferred_response": record.fields[preferred_rank],
            "least_preferred_response": record.fields[least_preferred_rank],
        })

# Now, "triplets" is a list of dictionaries, each containing a prompt and the associated
# preferred and less preferred responses
````

```{tip}
If you used the `RatingQuestion` instead, here's the corresponding code snippet:
```python
# Define an empty list to store the triplets
triplets = []

# Loop over all records in the dataset
for record in feedback.records:
    # Ensure that the record has responses
    if record.responses is None or len(record.responses) == 0:
        continue

    # Ensure the response has been submitted (not discarded)
    response = record.responses[0]

    if response.status == 'submitted':
        # Get the preferred response index from the feedback
        preferred_index = response.values["response_ranking"].value

        # Append the non-preferred response index
        less_preferred_index = 1 if preferred_index == 2 else 2

        # Construct the triplet and append to the list
        triplets.append({
            "prompt": record.fields["prompt"],
            "preferred_response": record.fields[f"response {preferred_index}"],
            "less_preferred_response": record.fields[f"response {less_preferred_index}"],
        })

# Now, "triplets" is a list of dictionaries, each containing a prompt and the associated
# preferred and less preferred responses
````

The final step is to prepare your dataset for training your reward model. This preparation depends on the chosen framework. [This guide](/practical_guides/fine_tune) provides a comprehensive overview of the options and corresponding data preparation methods.
