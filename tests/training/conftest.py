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

import argilla as rg
import pytest


@pytest.fixture
def dataset_token_classification(mocked_client):
    from datasets import load_dataset

    dataset = "gutenberg_spacy_ner"

    dataset_ds = load_dataset(
        "argilla/gutenberg_spacy-ner",
        split="train[:100]",
        # This revision does not includes the vectors info, so tests will pass
        revision="fff5f572e4cc3127f196f46ba3f9914c6fd0d763",
    )

    dataset_rb = rg.read_datasets(dataset_ds, task="TokenClassification")
    # Set annotations, required for training tests
    for rec in dataset_rb:
        # Strip off "score"
        rec.annotation = [prediction[:3] for prediction in rec.prediction]
        rec.annotation_agent = rec.prediction_agent
        rec.prediction = []
        rec.prediction_agent = None

    rg.delete(dataset)
    rg.log(name=dataset, records=dataset_rb)

    return dataset


@pytest.fixture
def dataset_text_classification(mocked_client):
    from datasets import load_dataset

    dataset = "banking_sentiment_setfit"

    dataset_ds = load_dataset(
        f"argilla/{dataset}",
        split="train[:100]",
    )
    dataset_rb = [rg.TextClassificationRecord(text=rec["text"], annotation=rec["label"]) for rec in dataset_ds]

    rg.delete(dataset)
    rg.log(name=dataset, records=dataset_rb)

    return dataset


@pytest.fixture
def dataset_text_classification_multi_label(mocked_client):
    from datasets import load_dataset

    dataset = "research_titles_multi_label"

    dataset_ds = load_dataset("argilla/research_titles_multi-label", split="train[:100]")

    dataset_rb = rg.read_datasets(dataset_ds, task="TextClassification")

    dataset_rb = [rec for rec in dataset_rb if rec.annotation]

    rg.delete(dataset)
    rg.log(name=dataset, records=dataset_rb)

    return dataset


@pytest.fixture
def dataset_text2text(mocked_client):
    from datasets import load_dataset

    dataset = "news_summary"

    dataset_ds = load_dataset("argilla/news-summary", split="train[:100]")

    records = []
    for entry in dataset_ds:
        records.append(rg.Text2TextRecord(text=entry["text"], annotation=entry["prediction"][0]["text"]))

    rg.delete(dataset)
    rg.log(name=dataset, records=records)

    return dataset
