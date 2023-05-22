# How-to Guide

This guide will help you with all the practical aspects of setting up an annotation project for training and fine-tuning LLMs using Argilla's Feedback Task Datasets. It covers everything from defining your task to collecting, organizing, and using the feedback effectively.


````{grid}  1 1 2 2
:class-container: tuto-section-2
```{grid-item-card} Define the task
:link: define_task.html

- Format records
- Define questions
- Write guidelines
```
```{grid-item-card} Set up your annotation team
:link: set_up_annotation_team.html

- Full overlap
- Zero overlap
- Controlled overlap
```
```{grid-item-card} Create and import a dataset
:link: create_and_import_dataset.html

- Argilla
- Hugging Face Hub
```
```{grid-item-card} Annotate Feedback datasets
:link: annotate_feedback_dataset.html

- Annotation Guidelines
- Annotation view
- Keyboard Shortcuts
```
```{grid-item-card} Collect responses
:link: collect_responses.html

- Measure and solve disagreements
  - Unifying ratings
  - Unifying texts
- Export or publish
```
```{grid-item-card} Fine-tune
:link: fine_tune.html

- RLHF
- Supervised
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