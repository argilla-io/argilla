# How-to Guide

This guide will help you with all the practical aspects of setting up an annotation project for training and fine-tuning LLMs using Argilla's Feedback Task Datasets. It covers everything from defining your task to collecting, organizing, and using the feedback effectively.


````{grid}  1 1 3 3
:class-container: tuto-section-2
```{grid-item-card} Create a Feedback Dataset
:link: create_dataset.html

Create a `FeedbackDataset` with `fields`, `questions`, and `guidelines`; and add `records` to it, based on your task.

```
```{grid-item-card} Set up your annotation team
:link: set_up_annotation_team.html

Organize your team efficiently and set up your dataset depending on the level of overlap: none, complete or partial.

```
```{grid-item-card} Import/Export a Feedback Dataset
:link: import_export_dataset.html

Easily import and export your `FeedbackTask` dataset from/to Argilla, HuggingFace Hub, or a combination of both. Or save the records in a local file.

```
```{grid-item-card} Annotate a Feedback Dataset
:link: annotate_dataset.html

Learn how to use the Argilla UI to submit feedback for `FeedbackTask` datasets, including shortcuts.

```
```{grid-item-card} Collect responses
:link: collect_responses.html

Load annotations from Argilla, visualize and solve disagreements. Finally, export your dataset or publish it in the Hugging Face Hub.

```
```{grid-item-card} Fine-tune
:link: fine_tune.html

Fine-tune an LLM with the feedback collected from Argilla.

```
````

![Feedback dataset snapshot](../../../_static/images/llms/snapshot-feedback-demo.png)

```{toctree}
:maxdepth: 2
:hidden:

create_dataset
set_up_annotation_team
import_export_dataset
annotate_dataset
collect_responses
fine_tune
```