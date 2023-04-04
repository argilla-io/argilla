---
title: SetFit
description: The ArgillaSetFitTrainer leverages the features of SetFit to train programmatically with Argilla.
links:
  - linkText: Argilla docs
    linkLink: https://docs.argilla.io/en/latest/guides/
  - linkText: SetFit docs
    linkLink: https://github.com/huggingface/setfit
---

*code snippet*

```python
from argilla.training import ArgillaTrainer

trainer = ArgillaTrainer(
    name="<my_dataset_name>",
    workspace="<my_workspace_name>",
    framework="setfit",
    train_size=0.8
)
trainer.update_config(max_epochs=10)
trainer.train(path="text-classification")
records = trainer.predict("The ArgillaTrainer is great!", as_argilla_records=True)
rg.log(records=records, name="<my_dataset_name>", workspace="<my_workspace_name>")
```

*`trainer.update_config(**kwargs)`*

```bash
# `setfit.SetFitModel`
pretrained_model_name_or_path = "all-MiniLM-L6-v2"
force_download = false
resume_download = false
proxies = none
token = none
cache_dir = none
local_files_only = false

# `setfit.SetFitTrainer`
metric = "accuracy"
num_iterations = 20
num_epochs = 1
learning_rate = 2e-5
batch_size = 16
seed = 42
use_amp = true
warmup_proportion = 0.1
distance_metric = `BatchHardTripletLossDistanceFunction.cosine_distance`
margin = 0.25
samples_per_label = 2
```
