---
# For reference on model card metadata, see the spec: https://github.com/huggingface/hub-docs/blob/main/datasetcard.md?plain=1
# Doc / guide: https://huggingface.co/docs/hub/datasets-cards
{{ card_data }}
---

# Dataset Card for {{ repo_id.split("/")[-1] }}

This dataset has been created with [Argilla](https://docs.argilla.io).

As shown in the sections below, this dataset can be loaded into Argilla as explained in [Load with Argilla](#load-with-argilla), or used directly with the `datasets` library in [Load with `datasets`](#load-with-datasets).

## Dataset Description

- **Homepage:** {{ homepage_url | default("https://argilla.io", true)}}
- **Repository:** {{ repo_url | default("https://github.com/argilla-io/argilla", true)}}
- **Paper:** {{ paper_url | default("", true)}}
- **Leaderboard:** {{ leaderboard_url | default("", true)}}
- **Point of Contact:** {{ point_of_contact | default("", true)}}

### Dataset Summary

This dataset contains:

* A dataset configuration file conforming to the Argilla dataset format named `argilla.yaml`. This configuration file will be used to configure the dataset when using the `FeedbackDataset.from_huggingface` method in Argilla.

* Dataset records in a format compatible with HuggingFace `datasets`. These records will be loaded automatically when using `FeedbackDataset.from_huggingface` and can be loaded independently using the `datasets` library via `load_dataset`.

* The [annotation guidelines](#annotation-guidelines) that have been used for building and curating the dataset, if they've been defined in Argilla.

### Load with Argilla

To load with Argilla, you'll just need to install Argilla as `pip install argilla --upgrade` and then use the following code:

```python
import argilla as rg

ds = rg.FeedbackDataset.from_huggingface("{{ repo_id }}")
```

### Load with `datasets`

To load this dataset with `datasets`, you'll just need to install `datasets` as `pip install datasets --upgrade` and then use the following code:

```python
from datasets import load_dataset

ds = load_dataset("{{ repo_id }}")
```

### Supported Tasks and Leaderboards

This dataset can contain [multiple fields, questions and responses](https://docs.argilla.io/en/latest/conceptual_guides/data_model.html#feedback-dataset) so it can be used for different NLP tasks, depending on the configuration. The dataset structure is described in the [Dataset Structure section](#dataset-structure).

There are no leaderboards associated with this dataset.

### Languages

{{ languages_section | default("[More Information Needed]", true)}}

## Dataset Structure

### Data in Argilla

The dataset is created in Argilla with: **fields**, **questions**, **suggestions**, and **guidelines**.

The **fields** are the dataset records themselves, for the moment just text fields are suppported. These are the ones that will be used to provide responses to the questions.

| Field Name | Title | Type | Required | Markdown |
| ---------- | ----- | ---- | -------- | -------- |
{% for field in argilla_fields %}| {{ field.name }} | {{ field.title }} | {{ field.type }} | {{ field.required }} | {{ field.use_markdown }} |
{% endfor %}

The **questions** are the questions that will be asked to the annotators. They can be of different types, such as rating, text, label_selection, multi_label_selection, or ranking.

| Question Name | Title | Type | Required | Description | Values/Labels |
| ------------- | ----- | ---- | -------- | ----------- | ------------- |
{% for question in argilla_questions %}| {{ question.name }} | {{ question.title }} | {{ question.type }} | {{ question.required }} | {{ question.description | default("N/A", true) }} | {% if question.type in ["rating", "label_selection", "multi_label_selection", "ranking"] %}{% if question.type in ["rating", "ranking"] %}{{ question.values | list }}{% else %}{{ question.labels | list }}{% endif %}{% else %}N/A{% endif %} |
{% endfor %}

**✨ NEW** Additionally, we also have **suggestions**, which are linked to the existing questions, and so on, named appending "-suggestion" and "-suggestion-metadata" to those, containing the value/s of the suggestion and its metadata, respectively. So on, the possible values are the same as in the table above.

Finally, the **guidelines** are just a plain string that can be used to provide instructions to the annotators. Find those in the [annotation guidelines](#annotation-guidelines) section.

### Data Instances

An example of a dataset instance in Argilla looks as follows:

```json
{{ argilla_record | tojson(indent=4) }}
```

While the same record in HuggingFace `datasets` looks as follows:

```json
{{ huggingface_record | tojson(indent=4) }}
```

### Data Fields

Among the dataset fields, we differentiate between the following:

* **Fields:** These are the dataset records themselves, for the moment just text fields are suppported. These are the ones that will be used to provide responses to the questions.
    {% for field in argilla_fields %}
    * {% if field.required == false %}(optional) {% endif %}**{{ field.name }}** is of type `{{ field.type }}`.{% endfor %}

* **Questions:** These are the questions that will be asked to the annotators. They can be of different types, such as `RatingQuestion`, `TextQuestion`, `LabelQuestion`, `MultiLabelQuestion`, and `RankingQuestion`.
    {% for question in argilla_questions %}
    * {% if question.required == false %}(optional) {% endif %}**{{ question.name }}** is of type `{{ question.type }}`{% if question.type in ["rating", "label_selection", "multi_label_selection", "ranking"] %} with the following allowed values {% if question.type in ["rating", "ranking"] %}{{ question.values | list }}{% else %}{{ question.labels | list }}{% endif %}{% endif %}{% if question.description %}, and description "{{ question.description }}"{% endif %}.{% endfor %}

* **✨ NEW** **Suggestions:** As of Argilla 1.13.0, the suggestions have been included to provide the annotators with suggestions to ease or assist during the annotation process. Suggestions are linked to the existing questions, are always optional, and contain not just the suggestion itself, but also the metadata linked to it, if applicable.
    {% for question in argilla_questions %}
    * (optional) **{{ question.name }}-suggestion** is of type `{{ question.type }}`{% if question.type in ["rating", "label_selection", "multi_label_selection", "ranking"] %} with the following allowed values {% if question.type in ["rating", "ranking"] %}{{ question.values | list }}{% else %}{{ question.labels | list }}{% endif %}{% endif %}.{% endfor %}

Additionally, we also have one more field which is optional and is the following:

* **external_id:** This is an optional field that can be used to provide an external ID for the dataset record. This can be useful if you want to link the dataset record to an external resource, such as a database or a file.

### Data Splits

The dataset contains a single split, which is `train`.

## Dataset Creation

### Curation Rationale

{{ curation_rationale_section | default("[More Information Needed]", true)}}

### Source Data

#### Initial Data Collection and Normalization

{{ data_collection_section | default("[More Information Needed]", true)}}

#### Who are the source language producers?

{{ source_language_producers_section | default("[More Information Needed]", true)}}

### Annotations

#### Annotation guidelines

{{ argilla_guidelines | default("[More Information Needed]", true)}}

#### Annotation process

{{ annotation_process_section | default("[More Information Needed]", true)}}

#### Who are the annotators?

{{ who_are_annotators_section | default("[More Information Needed]", true)}}

### Personal and Sensitive Information

{{ personal_and_sensitive_information_section | default("[More Information Needed]", true)}}

## Considerations for Using the Data

### Social Impact of Dataset

{{ social_impact_section | default("[More Information Needed]", true)}}

### Discussion of Biases

{{ discussion_of_biases_section | default("[More Information Needed]", true)}}

### Other Known Limitations

{{ known_limitations_section | default("[More Information Needed]", true)}}

## Additional Information

### Dataset Curators

{{ dataset_curators_section | default("[More Information Needed]", true)}}

### Licensing Information

{{ licensing_information_section | default("[More Information Needed]", true)}}

### Citation Information

{{ citation_information_section | default("[More Information Needed]", true)}}

### Contributions

{{ contributions_section | default("[More Information Needed]", true)}}