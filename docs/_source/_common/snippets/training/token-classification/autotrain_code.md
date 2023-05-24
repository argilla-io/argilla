---
title: AutoTrain (code)
description: Use Argilla, Datasets and Hugging Face AutoTrain Advanced with the ArgillaTrainer.
links:
  - linkText: Tutorial
    linkLink: https://www.argilla.io/blog/argilla-meets-autotrain/
  - linkText: AutoTrain Advanced docs
    linkLink: https://github.com/huggingface/autotrain-advanced
  - linkText: AutoTrain Advanced blog
    linkLink: https://huggingface.co/autotrain
---

*code snippet*

```python
from argilla.training import ArgillaTrainer

trainer = ArgillaTrainer(
    name="<my_dataset_name>",
    workspace="<my_workspace_name>",
    framework="autotrain",
    train_size=0.8
)
trainer.update_config(model="roberta-base", hub_model=[{"learning_rate": 0.0002}, {"learning_rate": 0.0003}])
trainer.train(output_dir="token-classification")
records = trainer.predict("The ArgillaTrainer is great!", as_argilla_records=True)
```

*update training config*

```python
trainer.update_config(
    model = "autotrain", # hub models like roberta-base
    autotrain = [{
        "source_language": "en",
        "num_models": 5
    }],
    hub_model = [{
        "learning_rate":  0.001,
        "optimizer": "adam",
        "scheduler": "linear",
        "train_batch_size": 8,
        "epochs": 10,
        "percentage_warmup": 0.1,
        "gradient_accumulation_steps": 1,
        "weight_decay": 0.1,
        "tasks": "text_binary_classification", # this is inferred from the dataset
    }]
)
```
