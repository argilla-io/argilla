# Tutorials

**Feedback Dataset**

```{include} /_common/feedback_dataset.md
```

Here you can find end-to-end examples to help you get started with curanting datasets and collecting feedback to fine-tune LLMs and other language models.

````{grid}  1 1 3 3
:class-container: tuto-section-2
```{grid-item-card} 🪄 Fine-tuning and evaluating GPT-3.5 with human feedback for RAG
:link: feedback/fine-tuning-openai-rag-feedback.html

Learn how to fine-tune and evaluate gpt3.5-turbo models with human feedback for RAG applications with LlamaIndex.

```
```{grid-item-card} 🖼️ Curate an instruction dataset for supervised fine-tuning
:link: feedback/curating-feedback-instructiondataset.html

Learn how to set up a project to curate a public dataset that can be used to fine-tune an instruction-following model.

```
```{grid-item-card} 🏆 Train a Reward Model for RLHF
:link: feedback/train-reward-model-rlhf.html

Learn how to collect comparison or human preference data and train a reward model with the trl library.

```
```{grid-item-card} ✨ Add zero-shot suggestions using SetFit
:link: feedback/labelling-feedback-setfit.html

Learn how to add suggestions to your Feedback Dataset using SetFit.

```
```{grid-item-card} 🎡 Create and annotate synthetic data with LLMs
:link: feedback/labelling-feedback-langchain-syntethic.html

Learn how to create synthetic data and annotations with OpenAI, LangChain, Transformers and Outlines.
```
```{grid-item-card} 🎛️ Fine-tune a SetFit model using the ArgillaTrainer
:link: feedback/trainer-feedback-setfit.html

Learn how to use the ArgillaTrainer to fine-tune your Feedback Dataset using Setfit.

```
````

**Other datasets**

```{include} /_common/other_datasets.md
```

Looking for more tutorials? Check out our [notebooks folder](/reference/notebooks)!

````{grid}  1 1 3 3
:class-container: tuto-section-2
```{grid-item-card} 🤯 Few-shot classification
:link: other_datasets/few_shot_learning_with_setfit.html

Learn how to use the `setfit` library to perform few-shot classification.

```

```{grid-item-card} 👂 Few shot text classification with active learning
:link: other_datasets/few_shot_text_classification_with_active_learning.html

Learn how to use the `setfit` and `small-text` libraries to perform few-shot text classification with active learning.

```
```{grid-item-card} 💨 Label data with semantic search
:link: other_datasets/label_data_with_semantic_search.html

Learn how to use the `sentence-transformers` library to label data with semantic search.

```
```{grid-item-card} 🧹 Find and clean label errors
:link: other_datasets/label_errors_cleanlab.html

Learn how to use the `cleanlab` library to find and clean label errors.

```
```{grid-item-card} 🐭 Weak supervision for NER
:link: other_datasets/weak_supervision_ner.html

Learn how to use the `snorkel` library to perform weak supervision for NER.
```
```{grid-item-card} 👮 Weak supervision for text classification with semantic search
:link: other_datasets/weak_supervision_text_classification_semantic_search.html

Learn how to use the `sentence-transformers` and `snorkel` to do weak supervision for text classification with semantic search.
```
````
<!--
```{toctree}
:hidden:

feedback/fine-tuning-openai-rag-feedback
feedback/curating-feedback-instructiondataset
feedback/train-reward-model-rlhf
feedback/labelling-feedback-setfit
feedback/trainer-feedback-setfit
feedback/labelling-feedback-langchain-syntethic

other_datasets/few_shot_learning_with_setfit
other_datasets/few_shot_text_classification_with_active_learning
other_datasets/label_data_with_semantic_search
other_datasets/label_errors_cleanlab
other_datasets/weak_supervision_ner
other_datasets/weak_supervision_text_classification_semantic_search
``` -->