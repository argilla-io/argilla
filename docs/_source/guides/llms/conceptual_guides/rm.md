# Collecting comparison data

This guide will help you set up workflows for collecting comparison data to train a reward model. The steps are: **create the dataset**, **add records**, **labelers rank responses**, **prepare the dataset**, and **train the reward model**.

<img src="../../../_static/images/llms/rm.svg" alt="Comparison collection for Reward Modeling" style="display:block;margin-left:auto;margin-right:auto;">

:::{note}
For a practical hands-on introduction, you may directly proceed to the How-to Guides or Examples section. This guide focuses on providing a detailed, conceptual description of the process.
:::

### Create the dataset

In this phase, you'll set up a dataset to gather ranked responses to each `prompt`.

First, let's configure a **dataset** using the Argilla Python SDK. This dataset will contain **questions** for labelers to answer. In this case, we want to collect ranked responses from our labelers. We’ll define a **RatingQuestion**:

```python
import argilla as rg

questions = [
    rg.RatingQuestion(
        name="response_ranking",
        title="Rank the accuracy of the responses (1: first response is more accurate, 2: second response is more accurate):",
        required=True
    )
]
```

:::{tip}
While the proposed setup in this guide is designed for comparing two responses, it is possible to include more than two responses for each prompt. This approach provides richer data for training your reward model, but increases the complexity of the task for the labelers. To include three responses per prompt, for instance, you would need to add additional fields for the extra responses and adjust the RatingQuestion to be: 

```python
rg.RatingQuestion(name="rankings", title="Rank the responses in terms of accuracy.", choices=["1", "2", "3"]).
```

Once the rankings have been collected, there's a unique way to process this data into prompt-response pairs for training your reward model. For instance, if response 1 was ranked as the best, you can form two triplets: `(prompt, response 1, response 2)` and `(prompt, response 1, response 3)`, indicating the model should prefer the first response over the second in each triplet.

This approach generates more diversified training examples. However, it doesn't presume any preference between the lower-ranked responses (response 2 and response 3 in this case), given that the labeler only ranked the best response. This method ensures that the model learns to prefer higher-ranked responses without making assumptions about preferences among lower-ranked ones.

Distributing the comparison collection task among several labelers can have additional benefits. While each labeler is asked to choose their preferred response for a given prompt, across multiple labelers we can potentially deduce preferences between all responses.

For example, suppose we have three responses for a given prompt: response 1, response 2, and response 3. If some labelers prefer response 1 over response 2, and others prefer response 2 over response 3, we can indirectly infer that response 1 is likely preferred over response 3, even if no single labeler directly compared these two responses.

This indirect comparison may not be as reliable as a direct comparison, as it depends on the consistency of labeler preferences. However, when aggregated across a large number of labelers and prompts, it can still provide valuable data for training the reward model.
:::

:::{note}
In a future release, Argilla will include a `RankingQuestion`, especifically tailored for this workflow.You can track the progress, provide feedback, and leave comments on [this GitHub issue]().
:::

The dataset consists of **records**. Each **record** is a data point that can be labeled by one or more labelers. A record has one or more **fields**. For this task, we need to present labelers with a prompt. We’ll define a **text field**:

```python
fields = [
    rg.TextField(name="prompt", required=True)
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

The aim of this phase is to create records with `prompts` and two generated `responses` to be pushed into Argilla for collecting human `rankings`.

Once you have configured the dataset, you need to add records and publish it for labelers. In this case, the records will contain three fields: the **prompt**, **response 1**, and **response 2**. The **prompt** and the two **responses** will be shown to labelers in the UI and we will ask them to rank the two responses. The most important questions at this step are: **how to generate the two responses** in order to maximize the quality and variety of the resulting LLM.

:::{tip}
Important features for the resulting dataset include diversity, consistent response style, and quality. These features must be considered when designing the data selection and collection processes.
:::

The responses can be generated using a pre-trained LLM, fine-tuned on a prior dataset. You can use different strategies to generate the responses, such as generating multiple responses and selecting two, or generating two responses with different parameters (e.g., temperature).

Assuming that you have a pre-trained LLM, here's how you can generate the responses:


```python
from transformers import GPTNeoForCausalLM, GPT2Tokenizer

# Load the model and tokenizer
model = GPTNeoForCausalLM.from_pretrained("your_finetuned_model")
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# Load your dataset of prompts
prompts = load_dataset('your_prompts_dataset', split=["train"])

records = []
for record in prompts:
    prompt = record["prompt"]
    # Generate two responses
    responses = []
    for _ in range(2):
        input_ids = tokenizer.encode(prompt, return_tensors='pt')
        output = model.generate(input_ids, max_length=100, num_return_sequences=1, temperature=1)
        decoded_output = tokenizer.decode(output[:, input_ids.shape[-1]:][0], skip_special_tokens=True)
        responses.append(decoded_output)

    record = rg.FeedbackRecord(fields={"prompt": prompt, "response 1": responses[0], "response 2": responses[1]})
    records.append(record)

# Add records to the dataset
dataset.add_records(records)

# This publishes the dataset and pushes the records into Argilla
dataset.push_to_argilla(name="my-dataset", workspace="my-workspace")

```

The above code will generate two responses for each prompt and push these records to Argilla. Labelers will see these prompts and responses, and rank the responses according to the instructions provided in the dataset.

:::{note}
The ranking task can be challenging for labelers if the two responses are very similar. Consider adjusting the parameters of the generation process (e.g., the temperature) to produce more varied responses.
:::

:::{tip}
As the field is rapidly evolving and lacking consensus, we suggest beginning with a small dataset of the highest quality. Argilla Feedback is built for iteration. Starting small allows for faster iteration: training is cheaper and faster, and the length of the feedback loop is reduced.
:::

## Labelers rank responses

The aim of this phase is to provide human rankings for pairs of responses to a given `prompt` using the Argilla UI.

Once you upload your dataset to Argilla, it becomes accessible via the Argilla UI. Argilla Feedback allows simultaneous feedback collection from multiple users, enhancing quality control. Each user with dataset access can give their feedback.

However, when resources are limited, workload distribution among various labelers is recommended. This strategy entails assigning each labeler a subset of records to rank. This [how-to guide](../practical_guides/set_up_annotation_team.html) provides detailed instructions on setting up these workload distribution options effectively.

For a comprehensive understanding of the Argilla UI's main features, refer to this [how-to guide](../practical_guides/annotate_dataset.html).

Prepare the dataset

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

Each record in feedback.records contains a responses attribute, which houses the feedback provided for that record. The structure of each response includes:

    - `user_id`: The Argilla user ID of the labeler.
    - `values`: The feedback provided by the labeler. This is formatted as a dictionary, with keys for each question and values holding the respective answers.
    - `status`: The status of the response, which can be either submitted or discarded. For our purposes, we're only interested in the submitted responses.

For datasets where each record has a single response (no annotation overlap), post-processing is straightforward as there's no need to resolve conflicts between different annotations. However, if annotation overlaps exist, conflict resolution becomes necessary. For strategies on conflict resolution, refer to this guide.

In addition, each record contains a fields attribute, which includes all the fields set during dataset creation. In this case, prompt, response 1, and response 2 are inputs for the reward model, with preference rankings attached.

Upon resolving conflicts, the aim is to have a list of records each indicating a preference for one response over the other to a prompt. These will be used for training the reward model.

For demonstration purposes, here is a step-by-step code snippet to create a dataset of triplets `(prompt, preferred response, less preferred response)` from a single dataset without overlapping annotations:

```python
# Define an empty list to store the triplets
triplets = []

# Loop over all records in the dataset
for record in feedback.records:

    # Ensure the response has been submitted (not discarded)
    if record['responses'][0]['status'] == 'submitted':

        # Get the preferred response index from the feedback
        preferred_index = record['responses']['values']['response_ranking']

        # Append the non-preferred response index
        less_preferred_index = 1 if preferred_index == 2 else 2

        # Construct the triplet and append to the list
        triplets.append({
            'prompt': record['fields']['prompt'],
            'preferred_response': record['fields'][f'response {preferred_index}'],
            'less_preferred_response': record['fields'][f'response {less_preferred_index}'],
        })

# Now, 'triplets' is a list of dictionaries, each containing a prompt and the associated
# preferred and less preferred responses
```


The final step is to prepare your dataset for training your reward model. This preparation depends on the chosen framework. This guide provides a comprehensive overview of the options and corresponding data preparation methods.
