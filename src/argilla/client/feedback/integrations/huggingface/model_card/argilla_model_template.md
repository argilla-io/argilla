---
# For reference on model card metadata, see the spec: https://github.com/huggingface/hub-docs/blob/main/modelcard.md?plain=1
# Doc / guide: https://huggingface.co/docs/hub/model-cards
{{ card_data }}
---

<!-- This model card has been generated automatically according to the information the `ArgillaTrainer` had access to. You
should probably proofread and complete it, then remove this comment. -->

# Model Card for *{{ model_name | default("Model ID", true) }}*

This model has been created with [Argilla](https://docs.argilla.io), trained with *{{ library_name }}*.

<!-- Provide a quick summary of what the model is/does. -->

{{ model_summary | default("", true) }}

## Model training

Training the model using the `ArgillaTrainer`:

```python
# Load the dataset:
dataset = FeedbackDataset.from_{% if _is_on_huggingface %}huggingface("{{ dataset_name }}"){% else %}argilla({% if dataset_name %}"{{ dataset_name }}"{% else %}"..."{% endif %}){% endif %}

# Create the training task:
{{ trainer_task_call }}

# Create the ArgillaTrainer:
trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="{{ framework }}",
    {%- if lang %}{{ "\n    " }}lang="{{ lang }}",{% endif %}
    {%- if model_id %}{{ "\n    " }}model="{{ model_id }}",{% endif %}
    {%- if tokenizer %}{{ "\n    " }}tokenizer={{ tokenizer }},{% endif %}
    {%- if train_size %}{{ "\n    " }}train_size={{ train_size }},{% endif %}
    {%- if seed %}{{ "\n    " }}seed={{ seed }},{% endif %}
    {%- if gpu_id %}{{ "\n    " }}gpu_id={{ gpu_id }},{% endif %}
    {%- if framework_kwargs %}{{ "\n    " }}framework_kwargs={{ framework_kwargs }},{% endif %}
)
{% if update_config_call %}{{ update_config_call }}{% endif %}
trainer.train(output_dir={{ output_dir }})
```

You can test the type of predictions of this model like so:

```python
{{ predict_call }}
```

## Model Details

### Model Description

<!-- Provide a longer summary of what this model is. -->

{{ model_description | default("", true) }}

- **Developed by:** {{ developers | default("[More Information Needed]", true)}}
- **Shared by [optional]:** {{ shared_by | default("[More Information Needed]", true)}}
- **Model type:** {{ model_type | default("[More Information Needed]", true)}}
- **Language(s) (NLP):** {{ language | default("[More Information Needed]", true)}}
- **License:** {{ license | default("[More Information Needed]", true)}}
- **Finetuned from model [optional]:** {{ finetuned_from | default("[More Information Needed]", true)}}

{%- if repo %}
### Model Sources [optional]

<!-- Provide the basic links for the model. -->

- **Repository:** {{ repo }}
{% endif %}

<!--
## Uses

*Address questions around how the model is intended to be used, including the foreseeable users of the model and those affected by the model.*
-->

<!--
### Direct Use

*This section is for the model use without fine-tuning or plugging into a larger ecosystem/app.*
-->

<!--
### Downstream Use [optional]

*This section is for the model use when fine-tuned for a task, or when plugged into a larger ecosystem/app*
-->

<!--
### Out-of-Scope Use

*This section addresses misuse, malicious use, and uses that the model will not work well for.*
-->

<!--
## Bias, Risks, and Limitations

*This section is meant to convey both technical and sociotechnical limitations.*
-->

<!--
### Recommendations

*This section is meant to convey recommendations with respect to the bias, risk, and technical limitations.*
-->

<!--
## Training Details

### Training Metrics

*Metrics related to the model training.*
-->

<!--
### Training Hyperparameters

- **Training regime:** (fp32, fp16 mixed precision, bf16 mixed precision, bf16 non-mixed precision, fp16 non-mixed precision, fp8 mixed precision)
-->

<!--
## Environmental Impact

*Total emissions (in grams of CO2eq) and additional considerations, such as electricity usage, go here. Edit the suggested text below accordingly*

Carbon emissions can be estimated using the [Machine Learning Impact calculator](https://mlco2.github.io/impact#compute) presented in [Lacoste et al. (2019)](https://arxiv.org/abs/1910.09700).

- **Hardware Type:** {{ hardware | default("[More Information Needed]", true)}}
- **Hours used:** {{ hours_used | default("[More Information Needed]", true)}}
- **Cloud Provider:** {{ cloud_provider | default("[More Information Needed]", true)}}
- **Compute Region:** {{ cloud_region | default("[More Information Needed]", true)}}
- **Carbon Emitted:** {{ co2_emitted | default("[More Information Needed]", true)}}
-->

## Technical Specifications [optional]

### Framework Versions

- Python: {{ version["python"] }}
- Argilla: {{ version["argilla"] }}

<!--
## Citation [optional]

*If there is a paper or blog post introducing the model, the APA and Bibtex information for that should go in this section.*

### BibTeX
-->

<!--
## Glossary [optional]

*If relevant, include terms and calculations in this section that can help readers understand the model or model card.*
-->

<!--
## Model Card Authors [optional]

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->
