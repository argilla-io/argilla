::::{tab-set}

:::{tab-item} Text classification
```python
import argilla as rg

ds = rg.FeedbackDataset.for_text_classification(
    labels=["positive", "negative"],
    multi_label=False,
    use_markdown=True,
    guidelines=None,
)
ds
# FeedbackDataset(
#   fields=[TextField(name="text", use_markdown=True)],
#   questions=[LabelQuestion(name="label", labels=["positive", "negative"])]
#   guidelines="<Guidelines for the task>",
# )
```
:::

:::{tab-item} Summarization
```python
import argilla as rg

ds = rg.FeedbackDataset.for_summarization(
    use_markdown=True,
    guidelines=None,
)
ds
# FeedbackDataset(
#   fields=[TextField(name="text", use_markdown=True)],
#   questions=[TextQuestion(name="summary", use_markdown=True)]
#   guidelines="<Guidelines for the task>",
# )
```
:::

:::{tab-item} Translation
```python
import argilla as rg

ds = rg.FeedbackDataset.for_translation(
    use_markdown=True,
    guidelines=None,
)
ds
# FeedbackDataset(
#   fields=[TextField(name="source", use_markdown=True)],
#   questions=[TextQuestion(name="target", use_markdown=True)]
#   guidelines="<Guidelines for the task>",
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
)
ds
# FeedbackDataset(
#   fields=[
#       TextField(name="premise", use_markdown=True),
#       TextField(name="hypothesis", use_markdown=True)
#   ],
#   questions=[
#       LabelQuestion(
#           name="label", labels=["entailment", "neutral", "contradiction"]
#      )
#   ]
#   guidelines="<Guidelines for the task>",
# )
```
:::

:::{tab-item} Sentence Similarity
```python
import argilla as rg

ds = rg.FeedbackDataset.for_sentence_similarity(
    rating_scale=10,
    use_markdown=True,
    guidelines=None,
)
ds
# FeedbackDataset(
#   fields=[
#       TextField(name="sentence-1", use_markdown=True),
#       TextField(name="sentence-2", use_markdown=True)
#   ],
#   questions=[
#       RatingQuestion(name="similarity", values=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
#   ]
#   guidelines="<Guidelines for the task>",
# )
```
:::

:::{tab-item} Extractive Question Answering
```python
import argilla as rg

ds = rg.FeedbackDataset.for_extractive_question_answering(
    use_markdown=True,
    guidelines=None,
)
ds
# FeedbackDataset(
#   fields=[
#       TextField(name="question", use_markdown=True),
#       TextField(name="context", use_markdown=True)
#   ],
#   questions=[
#       TextQuestion(name="answer", use_markdown=True)
#   ]
#   guidelines="<Guidelines for the task>",
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
)
ds
# FeedbackDataset(
#   fields=[
#       TextField(name="prompt", use_markdown=True),
#       TextField(name="context", use_markdown=True)
#   ],
#   questions=[
#       TextQuestion(name="response", use_markdown=True)
#   ]
#   guidelines="<Guidelines for the task>",
# )
```

:::{tab-item} Preference Modeling
```python
import argilla as rg

ds = rg.FeedbackDataset.for_preference_modeling(
    use_markdown=True,
    guidelines=None,
)
ds
# FeedbackDataset(
#   fields=[
#       TextField(name="prompt", use_markdown=True),
#       TextField(name="context", use_markdown=True),
#       TextField(name="response-1", use_markdown=True),
#       TextField(name="response-2", use_markdown=True),
#   ],
#   questions=[
#       LabelQuestion(name="preference", values=["response-1", "response-2"])
#   ]
#   guidelines="<Guidelines for the task>",
# )
```
:::

:::{tab-item} Proximal Policy Optimization (PPO)
```python
import argilla as rg

ds = rg.FeedbackDataset.for_proximal_policy_optimization(
    context=True,
    use_markdown=True,
    guidelines=None,
)
ds
# FeedbackDataset(
#   fields=[
#       TextField(name="prompt", use_markdown=True),
#       TextField(name="context", use_markdown=True)
#   ],
#   questions=[
#       TextQuestion(name="response", use_markdown=True)
:::

:::{tab-item} Direct Preference Optimization (DPO)
```python
import argilla as rg

ds = rg.FeedbackDataset.for_direct_preference_optimization(
    context=True,
    use_markdown=True,
    guidelines=None,
)
ds
# FeedbackDataset(
#   fields=[
#       TextField(name="prompt", use_markdown=True),
#       TextField(name="context", use_markdown=True)
#       TextField(name="response-1", use_markdown=True),
#       TextField(name="response-2", use_markdown=True),
#   ],
#   questions=[
#       LabelQuestion(name="preference", values=["response-1", "response-2"])
#   ]
#   guidelines="<Guidelines for the task>",
# )
```
:::

:::{tab-item} Retrieval-Augmented Generation (RAG)
```python
import argilla as rg

ds = rg.FeedbackDataset.for_retrieval_augmented_generation(
    number_of_retrievals=1,
    rating_scale=10,
    use_markdown=False,
    guidelines=None,
)
ds
# FeedbackDataset(
#   fields=[
#       TextField(name="prompt", use_markdown=True),
#       TextField(name="retrieved_document_1", use_markdown=True),
#       TextField(name="response", use_markdown=True),
#   ],
#   questions=[
#       RatingQuestion(name="retrieval_1_rating", values=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
#   ]
#   guidelines="<Guidelines for the task>",
# )
```
:::

::::
