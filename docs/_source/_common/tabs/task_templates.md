::::{tab-set}

:::{tab-item} Text Classification
```python
import argilla as rg

ds = rg.FeedbackDataset.for_text_classification(
    labels=["positive", "negative"],
    multi_label=False,
    use_markdown=True,
    guidelines=None,
    metadata_properties=None,
    vectors_settings=None,
)
ds
# FeedbackDataset(
#     fields=[
#         TextField(name="text", use_markdown=True)
#     ],
#     questions=[
#         LabelQuestion(name="label", labels=["positive", "negative"])
#     ],
#     guidelines="<Guidelines for the task>",
#     metadata_properties="<Metadata Properties>",
#     vectors_settings="<Vectors Settings>",
# )
```
:::

:::{tab-item} Summarization
```python
import argilla as rg

ds = rg.FeedbackDataset.for_summarization(
    use_markdown=True,
    guidelines=None,
    metadata_properties=None,
    vectors_settings=None,
)
ds
# FeedbackDataset(
#     fields=[
#         TextField(name="text", use_markdown=True)
#     ],
#     questions=[
#         TextQuestion(name="summary", use_markdown=True)
#     ],
#     guidelines="<Guidelines for the task>",
#     metadata_properties="<Metadata Properties>",
#     vectors_settings="<Vectors Settings>",
# )
```
:::

:::{tab-item} Translation
```python
import argilla as rg

ds = rg.FeedbackDataset.for_translation(
    use_markdown=True,
    guidelines=None,
    metadata_properties=None,
    vectors_settings=None,
)
ds
# FeedbackDataset(
#     fields=[
#         TextField(name="source", use_markdown=True)
#     ],
#     questions=[
#         TextQuestion(name="target", use_markdown=True)
#     ],
#     guidelines="<Guidelines for the task>",
#     metadata_properties="<Metadata Properties>",
#     vectors_settings="<Vectors Settings>",
# )
```
:::

:::{tab-item} Natural Language Inference (NLI)
```python
import argilla as rg

ds = rg.FeedbackDataset.for_natural_language_inference(
    labels=None
    use_markdown=True,
    guidelines=None,
    metadata_properties=None,
    vectors_settings=None,
)
ds
# FeedbackDataset(
#     fields=[
#         TextField(name="premise", use_markdown=True),
#         TextField(name="hypothesis", use_markdown=True)
#     ],
#     questions=[
#         LabelQuestion(name="label", labels=["entailment", "neutral", "contradiction"])
#     ],
#     guidelines="<Guidelines for the task>",
#     metadata_properties="<Metadata Properties>",
#     vectors_settings="<Vectors Settings>",
# )
```
:::

:::{tab-item} Sentence Similarity
```python
import argilla as rg

ds = rg.FeedbackDataset.for_sentence_similarity(
    rating_scale=7,
    use_markdown=True,
    guidelines=None,
    metadata_properties=None,
    vectors_settings=None,
)
ds
# FeedbackDataset(
#     fields=[
#         TextField(name="sentence-1", use_markdown=True),
#         TextField(name="sentence-2", use_markdown=True)
#     ],
#     questions=[
#         RatingQuestion(name="similarity", values=[1, 2, 3, 4, 5, 6, 7])
#     ],
#     guidelines="<Guidelines for the task>",
#     metadata_properties="<Metadata Properties>",
#     vectors_settings="<Vectors Settings>",
# )
```
:::

:::{tab-item} Extractive Question Answering
```python
import argilla as rg

ds = rg.FeedbackDataset.for_question_answering(
    use_markdown=True,
    guidelines=None,
    metadata_properties=None,
    vectors_settings=None,
)
ds
# FeedbackDataset(
#     fields=[
#         TextField(name="question", use_markdown=True),
#         TextField(name="context", use_markdown=True)
#     ],
#     questions=[
#         TextQuestion(name="answer", use_markdown=True)
#     ],
#     guidelines="<Guidelines for the task>",
#     metadata_properties="<Metadata Properties>",
#     vectors_settings="<Vectors Settings>",
# )
```
:::

:::{tab-item} Supervised Fine-tuning (SFT)
```python
import argilla as rg

ds = rg.FeedbackDataset.for_supervised_fine_tuning(
    context=True,
    use_markdown=True,
    guidelines=None,
    metadata_properties=None,
    vectors_settings=None,
)
ds
# FeedbackDataset(
#     fields=[
#         TextField(name="prompt", use_markdown=True),
#         TextField(name="context", use_markdown=True)
#     ],
#     questions=[
#         TextQuestion(name="response", use_markdown=True)
#     ],
#     guidelines="<Guidelines for the task>",
#     metadata_properties="<Metadata Properties>",
#     vectors_settings="<Vectors Settings>",
# )
```
:::

:::{tab-item} Preference Modeling
```python
import argilla as rg

ds = rg.FeedbackDataset.for_preference_modeling(
    number_of_responses=2,
    context=False,
    use_markdown=True,
    guidelines=None,
    metadata_properties=None,
    vectors_settings=None,
)
ds
# FeedbackDataset(
#     fields=[
#         TextField(name="prompt", use_markdown=True),
#         TextField(name="context", use_markdown=True),
#         TextField(name="response1", use_markdown=True),
#         TextField(name="response2", use_markdown=True),
#     ],
#     questions=[
#         RankingQuestion(name="preference", values=["Response 1", "Response 2"])
#     ],
#     guidelines="<Guidelines for the task>",
#     metadata_properties="<Metadata Properties>"
#     vectors_settings="<Vectors Settings>",
# )
```
:::

:::{tab-item} Proximal Policy Optimization (PPO)
```python
import argilla as rg

ds = rg.FeedbackDataset.for_proximal_policy_optimization(
    rating_scale=7,
    context=True,
    use_markdown=True,
    guidelines=None,
    metadata_properties=None,
    vectors_settings=None,
)
ds
# FeedbackDataset(
#     fields=[
#         TextField(name="prompt", use_markdown=True),
#         TextField(name="context", use_markdown=True)
#     ],
#     questions=[
#         TextQuestion(name="response", use_markdown=True)
#     ],
#     guidelines="<Guidelines for the task>",
#     metadata_properties="<Metadata Properties>",
#     vectors_settings="<Vectors Settings>",
# )
```
:::

:::{tab-item} Direct Preference Optimization (DPO)
```python
import argilla as rg

ds = rg.FeedbackDataset.for_direct_preference_optimization(
    number_of_responses=2,
    context=False,
    use_markdown=True,
    guidelines=None,
    metadata_properties=None,
    vectors_settings=None,
)
ds
# FeedbackDataset(
#     fields=[
#         TextField(name="prompt", use_markdown=True),
#         TextField(name="context", use_markdown=True),
#         TextField(name="response1", use_markdown=True),
#         TextField(name="response2", use_markdown=True),
#     ],
#     questions=[
#         RankingQuestion(name="preference", values=["Response 1", "Response 2"])
#     ],
#     guidelines="<Guidelines for the task>",
#     metadata_properties="<Metadata Properties>",
#     vectors_settings="<Vectors Settings>",
# )
```
:::

:::{tab-item} Retrieval-Augmented Generation (RAG)
```python
import argilla as rg

ds = rg.FeedbackDataset.for_retrieval_augmented_generation(
    number_of_retrievals=1,
    rating_scale=7,
    use_markdown=False,
    guidelines=None,
    metadata_properties=None,
    vectors_settings=None,
)
ds
# FeedbackDataset(
#     fields=[
#         TextField(name="query", use_markdown=False),
#         TextField(name="retrieved_document_1", use_markdown=False),
#     ],
#     questions=[
#         RatingQuestion(name="rating_retrieved_document_1", values=[1, 2, 3, 4, 5, 6, 7]),
#         TextQuestion(name="response", use_markdown=False),
#     ],
#     guidelines="<Guidelines for the task>",
#     metadata_properties="<Metadata Properties>",
#     vectors_settings="<Vectors Settings>",
# )
```
:::

:::{tab-item} Multi-Modal Classification
```python
import argilla as rg

ds = rg.FeedbackDataset.for_multi_modal_classification(
    labels=["video", "audio", "image"],
    multi_label=False,
    guidelines=None,
    metadata_properties=None,
    vectors_settings=None,
)
ds
# FeedbackDataset(
#     fields=[
#         TextField(name="content", use_markdown=True, required=True),
#     ],
#     questions=[
#         LabelQuestion(name="label", labels=["video", "audio", "image"])
#     ],
#     guidelines="<Guidelines for the task>",
#     metadata_properties="<Metadata Properties>",
#     vectors_settings="<Vectors Settings>",
# )
```
:::

:::{tab-item} Multi-Modal Transcription
```python
import argilla as rg

ds = rg.FeedbackDataset.for_multi_modal_transcription(
    guidelines=None,
    metadata_properties=None,
    vectors_settings=None,
)
ds
# FeedbackDataset(
#     fields=[
#         TextField(name="content", use_markdown=True, required=True),
#     ],
#     questions=[
#         TextQuestion(name="description", use_markdown=True, required=True)
#     ],
#     guidelines="<Guidelines for the task>",
#     metadata_properties="<Metadata Properties>",
#     vectors_settings="<Vectors Settings>",
# )
```
:::

::::
