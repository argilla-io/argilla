---
# For reference on model card metadata, see the spec: https://github.com/huggingface/hub-docs/blob/main/datasetcard.md?plain=1
# Doc / guide: https://huggingface.co/docs/hub/datasets-cards
{{ card_data }}
---

# Dataset Card for {{ repo_id.split("/")[-1] }}

{% if homepage_url %}
- **Homepage:** [{{ homepage_url }}]({{ homepage_url }})
{% endif %}
{% if repo_url %}
- **Repository:** [{{ repo_url }}]({{ repo_url }})
{% endif %}
{% if paper_url %}
- **Paper:** [{{ paper_url }}]({{ paper_url }})
{% endif %}
{% if leaderboard_url %}
- **Leaderboard:** [{{ leaderboard_url }}]({{ leaderboard_url }})
{% endif %}
{% if point_of_contact %}
- **Point of Contact:** {{ point_of_contact }}
{% endif %}

This dataset has been created with [Argilla](https://github.com/argilla-io/argilla). As shown in the sections below, this dataset can be loaded into your Argilla server as explained in [Load with Argilla](#load-with-argilla), or used directly with the `datasets` library in [Load with `datasets`](#load-with-datasets).


## Using this dataset with Argilla

To load with Argilla, you'll just need to install Argilla as `pip install argilla --upgrade` and then use the following code:

```python
import argilla as rg

ds = rg.Dataset.from_hub("{{ repo_id }}", settings="auto")
```

This will load the settings and records from the dataset repository and push them to you Argilla server for exploration and annotation.

## Using this dataset with `datasets`

To load the records of this dataset with `datasets`, you'll just need to install `datasets` as `pip install datasets --upgrade` and then use the following code:

```python
from datasets import load_dataset

ds = load_dataset("{{ repo_id }}")
```

This will only load the records of the dataset, but not the Argilla settings.

## Dataset Structure

This dataset repo contains:

* Dataset records in a format compatible with HuggingFace `datasets`. These records will be loaded automatically when using `rg.Dataset.from_hub` and can be loaded independently using the `datasets` library via `load_dataset`.
* The [annotation guidelines](#annotation-guidelines) that have been used for building and curating the dataset, if they've been defined in Argilla.
* A dataset configuration folder conforming to the Argilla dataset format in `.argilla`.

The dataset is created in Argilla with: **fields**, **questions**, **suggestions**, **metadata**, **vectors**, and **guidelines**.

### Fields

The **fields** are the features or text of a dataset's records. For example, the 'text' column of a text classification dataset of the 'prompt' column of an instruction following dataset.

| Field Name | Title | Type | Required | Markdown |
| ---------- | ----- | ---- | -------- | -------- |
{% for field in argilla_fields %}| {{ field.name }} | {{ field.title }} | {{ field.type }} | {{ field.required }} | {{ field.use_markdown }} |
{% endfor %}

### Questions

The **questions** are the questions that will be asked to the annotators. They can be of different types, such as rating, text, label_selection, multi_label_selection, or ranking.

| Question Name | Title | Type | Required | Description | Values/Labels |
| ------------- | ----- | ---- | -------- | ----------- | ------------- |
{% for question in argilla_questions %}| {{ question.name }} | {{ question.title }} | {{ question.type }} | {{ question.required }} | {{ question.description | default("N/A", true) }} | {% if question.type in ["rating", "label_selection", "multi_label_selection", "ranking"] %}{% if question.type in ["rating", "ranking"] %}{{ question.values | list }}{% else %}{{ question.labels | list }}{% endif %}{% else %}N/A{% endif %} |
{% endfor %}

<!-- check length of metadata properties -->
{% if argilla_metadata_properties %}
### Metadata

The **metadata** is a dictionary that can be used to provide additional information about the dataset record.
| Metadata Name | Title | Type | Values | Visible for Annotators |
| ------------- | ----- | ---- | ------ | ---------------------- |
{% for metadata in argilla_metadata_properties %} | {{ metadata.name }} | {{ metadata.title }} | {{ metadata.type }} | {% if metadata.values %}{{ metadata.values }}{% else %}{{ metadata.min }} - {{ metadata.max }}{% endif %} | {{ metadata.visible_for_annotators }} |
{% endfor %}
{% endif %}

{% if argilla_vectors_settings %}
### Vectors
The **vectors** contain a vector representation of the record that can be used in  search.

| Vector Name | Title | Dimensions |
|-------------|-------|------------|
{% for vector in argilla_vectors_settings %}| {{ vector.name }} | {{ vector.title }} | [1, {{ vector.dimensions }}] |
{% endfor %}
{% endif %}


### Data Instances

An example of a dataset instance in Argilla looks as follows:

```json
{{ argilla_record | tojson(indent=4) }}
```

While the same record in HuggingFace `datasets` looks as follows:

```json
{{ huggingface_record | tojson(indent=4) }}
```


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
