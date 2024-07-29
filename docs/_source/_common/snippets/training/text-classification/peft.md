---
title: Peft
description: The ArgillaPeftTrainer leverages the base features of transformers and uses the Low Rank Adaptation (LoRA) implementation of Parameter Efficient Fine-Tuning (PEFT).
links:
  - linkText: Argilla docs
    linkLink: https://docs.v1.argilla.io/en/practical_guides/fine_tune.html#text-classification
  - linkText: Transformers blog
    linkLink: https://huggingface.co/blog/peft
  - linkText: Transformers docss
    linkLink: https://huggingface.co/docs/peft/index
---

_code snippet_

```python
from argilla.training import ArgillaTrainer

trainer = ArgillaTrainer(
    name="<my_dataset_name>",
    workspace="<my_workspace_name>",
    framework="peft",
    train_size=0.8
)
trainer.update_config(lora_alpha=8, num_train_epochs=3)
trainer.train(output_dir="text-classification")
records = trainer.predict("The ArgillaTrainer is great!", as_argilla_records=True)
```

_update training config_

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
    init_lora_weights=True
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
