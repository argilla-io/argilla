# Examples

Here you can find end-to-end examples to help you get started with curanting datasets and collecting feedback to fine-tune LLMs.

````{grid}  1 1 3 3
:class-container: tuto-section-2
```{grid-item-card} Fine-tuning and evaluating GPT-3.5 with human feedback for RAG
:link: fine-tuning-openai-rag-feedback.html

Learn how to fine-tune and evaluate gpt3.5-turbo models with human feedback for RAG applications with LlamaIndex.

```
```{grid-item-card} Curate an instruction dataset for supervised fine-tuning
:link: curating-feedback-instructiondataset.html

Learn how to set up a project to curate a public dataset that can be used to fine-tune an instruction-following model.

```
```{grid-item-card} Train a Reward Model for RLHF
:link: train-reward-model-rlhf.html

Learn how to collect comparison or human preference data and train a reward model with the trl library.

```
```{grid-item-card} Add zero-shot suggestions using SetFit
:link: labelling-feedback-setfit.html

Learn how to add suggestions to your `FeedbackDataset` using SetFit.

```
```{grid-item-card} Create and annotate synthetic data with LLMs
:link: labelling-feedback-langchain-syntethic.html

Learn how to create synthetic data and annotations with OpenAI, LangChain, Transformers and Outlines.
```
```{grid-item-card} Fine-tune a SetFit model using the ArgillaTrainer
:link: trainer-feedback-setfit.html

Learn how to use the ArgillaTrainer to fine-tune your Feedback dataset using Setfit.

```
````

```{toctree}
:hidden:

fine-tuning-openai-rag-feedback
curating-feedback-instructiondataset
train-reward-model-rlhf
labelling-feedback-setfit
trainer-feedback-setfit
labelling-feedback-langchain-syntethic
```