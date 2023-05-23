# How-to Guide

This guide will help you with all the practical aspects of setting up an annotation project for training and fine-tuning LLMs using Argilla's Feedback Task Datasets. It covers everything from defining your task to collecting, organizing, and using the feedback effectively.


````{grid}  1 1 2 2
:class-container: tuto-section-2
```{grid-item-card} Define the task
:link: define_task.html

Format the records to show specific inputs, define questions for the task and add annotation guidelines.

```
```{grid-item-card} Set up your annotation team
:link: set_up_annotation_team.html

Organize your team efficiently and set up your dataset depending on the level of overlap: none, complete or partial.

```
```{grid-item-card} Create and import a dataset
:link: create_and_import_dataset.html

Add configurations to your dataset and import it. Copy existing datasets from Argilla or import them from the Hugging Face Hub.

```
```{grid-item-card} Annotate Feedback datasets
:link: annotate_feedback_dataset.html

Learn how to use the Feedback Task UI to submit feedback, including shortcuts.

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

define_task
set_up_annotation_team
create_and_import_dataset
annotate_feedback_dataset
collect_responses
fine_tune
```