# 🧐 Choose a dataset type

## FAQs

**What? Different datasets?**

First things first, Argilla offers two generations of datasets. The new `FeedbackDataset` and the older datasets called `DatasetForTextClassification`, `DatasetForTokenClassification`, and `DatasetForText2Text`.

**Why the new `FeedbackDataset`?**

In short, the `FeedbackDataset` is a fully configurable dataset that can be used for any NLP task including LLM-focused tasks. The older datasets are focused on a single NLP task. As a result, the `FeedbackDataset` is more flexible and can be used for a wider range of use cases including all NLP tasks of the older datasets. The older datasets are more feature-rich in certain points but no new features are introduced, on the other hand, the `FeedbackDataset` is currently less feature-rich in certain points but new features will actively be added over time.

**Will the older datasets be deprecated?**

We will continue to maintain the older datasets for the foreseeable future, but we recommend using the new `FeedbackDataset`, which is going to be the core of Argilla 2.0.

**When should I use older datasets?**

At the moment, the older datasets are better when doing basic Text Classification or Token Classification. They provide full support for `metadata-filters`, `bulk-annotation`, `weak supervision`, `active learning` and `vector search`.

**When should I use `FeedbackDataset` better?**

The `FeedbackDataset` is better when you need to do more `complex tasks` that need to be represented in `one coherent UI`. This is extremely useful for `LLM` workflows where you need to do `multiple tasks` on the same record. The `FeedbackDataset` also supports `multiple annotators` per record, `customizable tasks` and `synchronization with a database`. However, it does not support `weak supervision` or `active learning` yet.

**When will all the cool features of the older datasets be available in the `FeedbackDataset`?**

We are working on it! We will be adding new features to the `FeedbackDataset` over time. If you need a specific feature, please let us know on [GitHub](https://github.com/argilla-io/argilla/issues) or Slack so we can prioritize it.

## Table comparison

### NLP Tasks

| Task / Dataset                    | FeedbackDataset 	| Older datasets 	|
|-------------------------------	|-----------------	|-------------------|
| Text classification           	| ✔️               	| ✔️                  |
| Token classification          	| ✔️               	| ✔️                  |
| Summarization                  	| ✔️               	| ✔️                   |
| Translation                  	    | ✔️               	| ✔️                   |
| NLI                  	            | ✔️               	| ✔️                   |
| Sentence Similarity               | ✔️               	|                              	|
| Question Answering               	| ✔️               	|                              	|
| RLHF (SFT)               	| ✔️               	|                              	|
| RLHF (RM)               	| ✔️               	|                              	|
| RLHF (PPO)               	| ✔️               	|                              	|
| RLHF (DPO)               	| ✔️               	|                              	|
| RAG               	| ✔️               	|                              	|
| Image support               	| ✔️               	|                              	|
| Overlapping spans           	|✔️                	|                  |
| And many more               	| ✔️               	|                              	|

### Annotation workflows

| Task / Dataset                    | FeedbackDataset 	| Older datasets 	|
|-------------------------------	|-----------------	|-------------------|
| bulk annotation           	|✔️                	| ✔️                  |
| vector search          	|✔️                 	| ✔️                  |
| active learning                     	|                	| ✔️                   |
| weak supervision               	|                	| ✔️                             	|

### User and team management

| Features                      	| FeedbackDataset 	| Older datasets 	|
|-------------------------------	|-----------------	|-------------------|
| Multiple annotators per record 	| ✔️               	|                    |
| Multiple-tasks in one UI      	| ✔️               	|                    |
| Synchronization with database 	| ✔️               	|                    |

### UI Sorting and filtering and querying

| Features                      	| FeedbackDataset 	| Older datasets 	|
|-------------------------------	|-----------------	|-------------------|
| Record status filters 	| ✔️               	| ✔️                   |
| Text query 	            | ✔️               	| ✔️                   |
| Metadata filters       	| ✔️               	| ✔️                   |
| Sorting 	                | ✔️             	| ✔️                   |
| Prediction filters 	            |✔️                	| ✔️                   |
| Annotation filters 	            |✔️               	| ✔️                   |
| Similarity search 	            |✔️                	| ✔️                   |