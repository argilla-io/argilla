---
title: Transformers
description: The ArgillaTransformersTrainer leverages the features of transformers to train programmatically with Argilla.
links:
  - linkText: Argilla docs
    linkLink: https://docs.v1.argilla.io/en/latest/practical_guides/fine_tune.html#token-classification
  - linkText: Transformers docs
    linkLink: https://huggingface.co/docs/transformers/training
---

*code snippet*

```python
from argilla.training import ArgillaTrainer

trainer = ArgillaTrainer(
    name="<my_dataset_name>",
    workspace="<my_workspace_name>",
    framework="transformers",
    train_size=0.8
)
trainer.update_config(num_train_epochs=10)
trainer.train(output_dir="token-classification")
records = trainer.predict("The ArgillaTrainer is great!", as_argilla_records=True)
```

*update training config*

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
