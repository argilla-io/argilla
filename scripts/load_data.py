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

import sys
import time

import pandas as pd
import requests
from datasets import load_dataset

import argilla as rg
from argilla.labeling.text_classification import Rule, add_rules


def load_datasets():
    # This is the code that you want to execute when the endpoint is available
    api_key = sys.argv[-1]
    rg.init(api_key=api_key, workspace="team")

    # load dataset from json
    my_dataframe = pd.read_json(
        "https://raw.githubusercontent.com/recognai/datasets/main/sst-sentimentclassification.json"
    )

    # convert pandas dataframe to DatasetForTextClassification
    dataset_rg = rg.DatasetForTextClassification.from_pandas(my_dataframe)

    # Define labeling schema to avoid UI user modification
    settings = rg.TextClassificationSettings(label_schema={"POSITIVE", "NEGATIVE"})
    rg.configure_dataset(name="sst-sentiment-explainability", settings=settings)

    # log the dataset
    rg.log(
        dataset_rg,
        name="sst-sentiment-explainability",
        tags={
            "description": "The sst2 sentiment dataset with predictions from a pretrained pipeline and explanations "
            "from Transformers Interpret. "
        },
    )

    dataset = load_dataset("argilla/news-summary", split="train").select(range(100))
    dataset_rg = rg.read_datasets(dataset, task="Text2Text")

    # log the dataset
    rg.log(
        dataset_rg,
        name="news-text-summarization",
        tags={
            "description": "A text summarization dataset with news pieces and their predicted summaries."
        },
    )

    # Read dataset from Hub
    dataset_rg = rg.read_datasets(
        load_dataset("argilla/agnews_weak_labeling", split="train"),
        task="TextClassification",
    )

    # Define labeling schema to avoid UI user modification
    settings = rg.TextClassificationSettings(
        label_schema={"World", "Sports", "Sci/Tech", "Business"}
    )
    rg.configure_dataset(name="news-programmatic-labeling", settings=settings)

    # log the dataset
    rg.log(
        dataset_rg,
        name="news-programmatic-labeling",
        tags={
            "description": "The AG News with programmatic labeling rules (see weak labeling mode in the UI)."
        },
    )

    # define queries and patterns for each category (using ES DSL)
    queries = [
        (["money", "financ*", "dollar*"], "Business"),
        (["war", "gov*", "minister*", "conflict"], "World"),
        (["*ball", "sport*", "game", "play*"], "Sports"),
        (["sci*", "techno*", "computer*", "software", "web"], "Sci/Tech"),
    ]

    # define rules
    rules = [
        Rule(query=term, label=label) for terms, label in queries for term in terms
    ]

    # add rules to the dataset
    add_rules(dataset="news-programmatic-labeling", rules=rules)

    # load dataset from the hub
    dataset = load_dataset("argilla/gutenberg_spacy-ner", split="train")

    # read in dataset, assuming it's a dataset for token classification
    dataset_rg = rg.read_datasets(dataset, task="TokenClassification")

    # Define labeling schema to avoid UI user modification
    labels = {
        "CARDINAL",
        "DATE",
        "EVENT",
        "FAC",
        "GPE",
        "LANGUAGE",
        "LAW",
        "LOC",
        "MONEY",
        "NORP",
        "ORDINAL",
        "ORG",
        "PERCENT",
        "PERSON",
        "PRODUCT",
        "QUANTITY",
        "TIME",
        "WORK_OF_ART",
    }
    settings = rg.TokenClassificationSettings(label_schema=labels)
    rg.configure_dataset(name="gutenberg_spacy-ner-monitoring", settings=settings)

    # log the dataset
    rg.log(
        dataset_rg,
        "gutenberg_spacy-ner-monitoring",
        tags={
            "description": "A dataset containing text from books with predictions from two spaCy NER pre-trained "
            "models. "
        },
    )


if __name__ == "__main__":
    while True:
        try:
            response = requests.get("http://0.0.0.0:6900/")
            if response.status_code == 200:
                load_datasets()
                break
        except requests.exceptions.ConnectionError:
            pass
        except Exception as e:
            print(e)
            time.sleep(10)
            pass

        time.sleep(5)
