#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os

import evaluate
import torch
from peft import (
    LoraConfig,
    get_peft_model,
)
from torch.optim import AdamW
from torch.utils.data import DataLoader
from tqdm import tqdm
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    get_linear_schedule_with_warmup,
)

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
batch_size = 32
task = "mrpc"
# peft_type = PeftType.LORA
device = "mps"
num_epochs = 1
lr = 3e-4

lr = 3e-4

model_name_or_path = "roberta-base"

if any(k in model_name_or_path for k in ("gpt", "opt", "bloom")):
    padding_side = "left"
else:
    padding_side = "right"

tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, padding_side=padding_side)
if getattr(tokenizer, "pad_token_id") is None:
    tokenizer.pad_token_id = tokenizer.eos_token_id

# dataset_name = "glue"
# datasets = load_dataset(dataset_name, task)
# metric = evaluate.load(dataset_name, task)
import os

import argilla as rg

os.environ["AUTOTRAIN_USERNAME"] = "argilla"
rg.init(api_url=os.environ.get("ARGILLA_API_URL_PRO"), api_key=os.environ.get("ARGILLA_API_KEY_PRO"))
rg_ds = rg.load("basf-text-plumber", "basf", limit=100, query="status: Validated")
datasets = rg_ds.prepare_for_training("transformers", train_size=0.8)


def tokenize_function(examples):
    # max_length=None => use the model max length (it's actually the default)
    return tokenizer(examples["text"], truncation=True, max_length=None)
    # return tokenizer(examples["sentence1"], examples["sentence2"], truncation=True, max_length=None)


tokenized_datasets = datasets.map(
    tokenize_function,
    batched=True,
    remove_columns=["id", "text"],
    # remove_columns=["idx", "sentence1", "sentence2"],
)

# We also rename the 'label' column to 'labels' which is the expected name for labels by the models of the
# transformers library
tokenized_datasets = tokenized_datasets.rename_column("label", "labels")


def collate_fn(examples):
    output = tokenizer.pad(examples, padding="longest", return_tensors="pt")

    return output


# Instantiate dataloaders.
train_dataloader = DataLoader(tokenized_datasets["train"], shuffle=True, collate_fn=collate_fn, batch_size=batch_size)
eval_dataloader = DataLoader(tokenized_datasets["test"], shuffle=False, collate_fn=collate_fn, batch_size=batch_size)

peft_config = LoraConfig(task_type="SEQ_CLS", inference_mode=False, r=8, lora_alpha=16, lora_dropout=0.1)  # TOKEN_CLS
model = AutoModelForSequenceClassification.from_pretrained(model_name_or_path, return_dict=True)
model = get_peft_model(model, peft_config)
model.print_trainable_parameters()
model

optimizer = AdamW(params=model.parameters(), lr=lr)

# Instantiate scheduler
lr_scheduler = get_linear_schedule_with_warmup(
    optimizer=optimizer,
    num_warmup_steps=0.06 * (len(train_dataloader) * num_epochs),
    num_training_steps=(len(train_dataloader) * num_epochs),
)
import numpy as np

metric = evaluate.load("f1")


def compute_metrics(eval_pred):
    """Computes accuracy on a batch of predictions"""
    predictions = np.argmax(eval_pred.predictions, axis=1)
    return metric.compute(predictions=predictions, references=eval_pred.label_ids)


# metric = evaluate.load("f1")
# model.to(device)
# for epoch in range(num_epochs):
#     model.train()
#     for step, batch in enumerate(tqdm(train_dataloader)):
#         batch.to(device)
#         outputs = model(**batch)
#         loss = outputs.loss
#         loss.backward()
#         optimizer.step()
#         lr_scheduler.step()
#         optimizer.zero_grad()

#     model.eval()
#     for step, batch in enumerate(tqdm(eval_dataloader)):
#         batch.to(device)
#         with torch.no_grad():
#             outputs = model(**batch)
#         predictions = outputs.logits.argmax(dim=-1)
#         predictions, references = predictions, batch["labels"]
#         metric.add_batch(
#             predictions=predictions,
#             references=references,
#         )

#     eval_metric = metric.compute()
#     print(f"epoch {epoch}:", eval_metric)

args = TrainingArguments(
    "finetuned-lora-food101",
    remove_unused_columns=False,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=lr,
    per_device_train_batch_size=batch_size,
    gradient_accumulation_steps=4,
    per_device_eval_batch_size=batch_size,
    num_train_epochs=num_epochs,
    logging_steps=1,
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    # push_to_hub=True,
    label_names=["labels"],
)

trainer = Trainer(
    model,
    args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["test"],
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
    data_collator=collate_fn,
)
trainer.train()
metric = evaluate.load("f1")
model.to(device)
for epoch in range(num_epochs):
    model.train()
    for step, batch in enumerate(tqdm(train_dataloader)):
        batch.to(device)
        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        lr_scheduler.step()
        optimizer.zero_grad()

    model.eval()
    for step, batch in enumerate(tqdm(eval_dataloader)):
        batch.to(device)
        with torch.no_grad():
            outputs = model(**batch)
        predictions = outputs.logits.argmax(dim=-1)
        predictions, references = predictions, batch["labels"]
        metric.add_batch(
            predictions=predictions,
            references=references,
        )

    eval_metric = metric.compute()
    print(f"epoch {epoch}:", eval_metric)
