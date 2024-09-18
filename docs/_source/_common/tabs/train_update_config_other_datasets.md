::::{tab-set}

:::{tab-item} OpenAI

```python
# `OpenAI.FineTune`
trainer.update_config(
    training_file = None,
    validation_file = None,
    model = "gpt-3.5-turbo-0613",
    hyperparameters = {"n_epochs": 1},
    suffix = None
)

# `OpenAI.FineTune` (legacy)
trainer.update_config(
    training_file = None,
    validation_file = None,
    model = "curie",
    n_epochs = 2,
    batch_size = None,
    learning_rate_multiplier = 0.1,
    prompt_loss_weight = 0.1,
    compute_classification_metrics = False,
    classification_n_classes = None,
    classification_positive_class = None,
    classification_betas = None,
    suffix = None
)
```
:::


:::{tab-item} SetFit

```python
# `setfit.SetFitModel`
trainer.update_config(
    pretrained_model_name_or_path = "all-MiniLM-L6-v2",
    force_download = False,
    resume_download = False,
    proxies = None,
    token = None,
    cache_dir = None,
    local_files_only = False
)
# `setfit.SetFitTrainer`
trainer.update_config(
    metric = "accuracy",
    num_iterations = 20,
    num_epochs = 1,
    learning_rate = 2e-5,
    batch_size = 16,
    seed = 42,
    use_amp = True,
    warmup_proportion = 0.1,
    distance_metric = "BatchHardTripletLossDistanceFunction.cosine_distance",
    margin = 0.25,
    samples_per_label = 2
)
```
:::

:::{tab-item} spaCy

```python
# `spacy.training`
trainer.update_config(
    dev_corpus = "corpora.dev",
    train_corpus = "corpora.train",
    seed = 42,
    gpu_allocator = 0,
    accumulate_gradient = 1,
    patience = 1600,
    max_epochs = 0,
    max_steps = 20000,
    eval_frequency = 200,
    frozen_components = [],
    annotating_components = [],
    before_to_disk = None,
    before_update = None
)
```
:::

:::{tab-item} Transformers

```python
# `transformers.AutoModelForTextClassification`
trainer.update_config(
    pretrained_model_name_or_path = "distilbert-base-uncased",
    force_download = False,
    resume_download = False,
    proxies = None,
    token = None,
    cache_dir = None,
    local_files_only = False
)
# `transformers.TrainingArguments`
trainer.update_config(
    per_device_train_batch_size = 8,
    per_device_eval_batch_size = 8,
    gradient_accumulation_steps = 1,
    learning_rate = 5e-5,
    weight_decay = 0,
    adam_beta1 = 0.9,
    adam_beta2 = 0.9,
    adam_epsilon = 1e-8,
    max_grad_norm = 1,
    learning_rate = 5e-5,
    num_train_epochs = 3,
    max_steps = 0,
    log_level = "passive",
    logging_strategy = "steps",
    save_strategy = "steps",
    save_steps = 500,
    seed = 42,
    push_to_hub = False,
    hub_model_id = "user_name/output_dir_name",
    hub_strategy = "every_save",
    hub_token = "1234",
    hub_private_repo = False
)
```
:::

:::{tab-item} Peft (LoRA)

```python
# `peft.LoraConfig`
trainer.update_config(
    r=8,
    target_modules=None,
    lora_alpha=16,
    lora_dropout=0.1,
    fan_in_fan_out=False,
    bias="none",
    inference_mode=False,
    modules_to_save=None,
    init_lora_weights=True,
)
# `transformers.AutoModelForTextClassification`
trainer.update_config(
    pretrained_model_name_or_path = "distilbert-base-uncased",
    force_download = False,
    resume_download = False,
    proxies = None,
    token = None,
    cache_dir = None,
    local_files_only = False
)
# `transformers.TrainingArguments`
trainer.update_config(
    per_device_train_batch_size = 8,
    per_device_eval_batch_size = 8,
    gradient_accumulation_steps = 1,
    learning_rate = 5e-5,
    weight_decay = 0,
    adam_beta1 = 0.9,
    adam_beta2 = 0.9,
    adam_epsilon = 1e-8,
    max_grad_norm = 1,
    learning_rate = 5e-5,
    num_train_epochs = 3,
    max_steps = 0,
    log_level = "passive",
    logging_strategy = "steps",
    save_strategy = "steps",
    save_steps = 500,
    seed = 42,
    push_to_hub = False,
    hub_model_id = "user_name/output_dir_name",
    hub_strategy = "every_save",
    hub_token = "1234",
    hub_private_repo = False
)
```
:::


:::{tab-item} SpanMarker

```python
# `SpanMarkerConfig`
trainer.update_config(
    pretrained_model_name_or_path = "distilbert-base-cased"
    model_max_length = 256,
    marker_max_length = 128,
    entity_max_length = 8,
)
# `transformers.TrainingArguments`
trainer.update_config(
    per_device_train_batch_size = 8,
    per_device_eval_batch_size = 8,
    gradient_accumulation_steps = 1,
    learning_rate = 5e-5,
    weight_decay = 0,
    adam_beta1 = 0.9,
    adam_beta2 = 0.9,
    adam_epsilon = 1e-8,
    max_grad_norm = 1,
    learning_rate = 5e-5,
    num_train_epochs = 3,
    max_steps = 0,
    log_level = "passive",
    logging_strategy = "steps",
    save_strategy = "steps",
    save_steps = 500,
    seed = 42,
    push_to_hub = False,
    hub_model_id = "user_name/output_dir_name",
    hub_strategy = "every_save",
    hub_token = "1234",
    hub_private_repo = False
)
```
:::

::::