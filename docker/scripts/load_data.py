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
from typing import Union

import argilla as rg
import pandas as pd
import requests
from argilla.labeling.text_classification import Rule, add_rules
from datasets import load_dataset


class LoadDatasets:
    def __init__(self, api_key: str):
        rg.init(api_key=api_key)

    @staticmethod
    def load_sst_sentiment_explainability():
        print("Loading Sst-sentiment-explainability dataset")

        # Load dataset from json
        my_dataframe = pd.read_json(
            "https://raw.githubusercontent.com/recognai/datasets/main/sst-sentimentclassification.json"
        )

        # Convert pandas dataframe to DatasetForTextClassification
        dataset_rg = rg.DatasetForTextClassification.from_pandas(my_dataframe)

        # Define labeling schema to avoid UI user modification
        settings = rg.TextClassificationSettings(label_schema={"POSITIVE", "NEGATIVE"})
        rg.configure_dataset(name="sst-sentiment-explainability", settings=settings)

        # Log the dataset
        rg.log(
            dataset_rg,
            name="sst-sentiment-explainability",
            tags={
                "description": "The sst2 sentiment dataset with predictions from a pretrained pipeline and "
                "explanations from Transformers Interpret."
            },
        )

    @staticmethod
    def load_news_text_summarization():
        print("Loading News-text-summarization dataset")

        # Load dataset from hub
        dataset = load_dataset("argilla/news-summary", split="train")
        dataset_rg = rg.read_datasets(dataset, task="Text2Text")

        # Log the dataset
        rg.log(
            dataset_rg,
            name="news-text-summarization",
            tags={"description": "A text summarization dataset with news pieces and their predicted summaries."},
        )

    @staticmethod
    def load_news_programmatic_labeling():
        print("Loading News-programmatic-labeling dataset")

        # Read and load dataset from Hub
        dataset_rg = rg.read_datasets(
            load_dataset("argilla/agnews_weak_labeling", split="train"),
            task="TextClassification",
        )

        # Define labeling schema to avoid UI user modification
        settings = rg.TextClassificationSettings(label_schema={"World", "Sports", "Sci/Tech", "Business"})
        rg.configure_dataset(name="news-programmatic-labeling", settings=settings)

        # Log the dataset
        rg.log(
            dataset_rg,
            name="news-programmatic-labeling",
            tags={"description": "The AG News with programmatic labeling rules (see weak labeling mode in the UI)."},
        )

        # Define queries and patterns for each category (using Elasticsearch DSL)
        queries = [
            (["money", "financ*", "dollar*"], "Business"),
            (["war", "gov*", "minister*", "conflict"], "World"),
            (["*ball", "sport*", "game", "play*"], "Sports"),
            (["sci*", "techno*", "computer*", "software", "web"], "Sci/Tech"),
        ]

        # Define rules
        rules = [Rule(query=term, label=label) for terms, label in queries for term in terms]

        # Add rules to the dataset
        add_rules(dataset="news-programmatic-labeling", rules=rules)

    @staticmethod
    def load_gutenberg_spacy_ner_monitoring():
        print("Loading Gutenberg_spacy-ner-monitoring dataset")

        # Load dataset from the hub
        dataset = load_dataset("argilla/gutenberg_spacy-ner", split="train")

        # Read in dataset, assuming it's a dataset for token classification
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

        # Log the dataset
        rg.log(
            dataset_rg,
            "gutenberg_spacy-ner-monitoring",
            tags={
                "description": "A dataset containing text from books with predictions from two spaCy NER pre-trained "
                "models. "
            },
        )

    @staticmethod
    def load_feedback_dataset_from_huggingface(repo_id: str, split: str = "train", samples: int = 100):
        print(f"Loading {repo_id} dataset")

        # Load dataset from the hub
        dataset = rg.FeedbackDataset.from_huggingface(
            repo_id=repo_id, split=f"{split}{f'[:{samples}]' if samples else ''}"
        )

        # Remove the `responses` from every `FeedbackRecord` to upload just the `fields`
        for record in dataset.records:
            record.responses = []

        dataset.push_to_argilla(name=repo_id.split("/")[-1])

    @staticmethod
    def load_mock_dataset_for_filter_metadata():
        print("Loading Mock dataset for metadata properties test")
        import random

        import argilla as rg

        dataset = rg.FeedbackDataset.from_huggingface("argilla/oasst_response_quality", split="train")

        records = dataset.records[:400]

        for record in records:
            record.metadata.update(
                {
                    "terms-prop": random.choice("abc"),
                    "int-prop": random.randint(-10, 100),
                    "float-prop": random.uniform(0, 100),
                }
            )
        meta_ds = rg.FeedbackDataset(
            fields=dataset.fields,
            questions=dataset.questions,
            metadata_properties=[
                rg.TermsMetadataProperty(name="terms-prop", values=["a", "b", "c"]),
                rg.IntegerMetadataProperty(name="int-prop", min=-10, max=100),
                rg.FloatMetadataProperty(name="float-prop", min=0.0, max=100),
            ],
        )

        meta_ds.add_records(records)
        meta_ds.push_to_argilla("dataset-with-metadata-properties")

    @staticmethod
    def build_error_analysis_record(
        row: pd.Series, legacy: bool = False
    ) -> Union[rg.FeedbackRecord, rg.TextClassificationRecord]:
        fields = {
            "user-message-1": row["HumanMessage1"],
            "llm-output": f"```json\n{row['llm_output']}\n```",
            "ai-message": row["AIMessage"],
            "function-message": row["FunctionMessage"],
            "system-message": "You are an AI assistant name ACME",
            "langsmith-url": f"https://smith.langchain.com/o/{row['parent_id']}",
        }
        metadata = {
            "correctness-langsmith": row["correctness_langsmith"],
            "model-name": row["model_name"],
            "temperature": row["temperature"],
            "max-tokens": row["max_tokens"],
            "cpu-user": row["cpu_time_user"],
            "cpu-system": row["cpu_time_system"],
            "library-version": row["library_version"],
        }

        if legacy:
            return rg.TextClassificationRecord(
                inputs=fields, metadata=metadata, vectors=eval(row["vectors"]), multi_label=True
            )
        return rg.FeedbackRecord(fields=fields, metadata=metadata)

    @staticmethod
    def load_error_analysis():
        print("Loading Error Analysis dataset as a `FeedbackDataset` (Alpha)")
        df = pd.read_csv("https://raw.githubusercontent.com/argilla-io/dataset_examples/main/synthetic_data_v2.csv")

        fields = [
            rg.TextField(name="user-message-1", use_markdown=True),
            rg.TextField(name="llm-output", use_markdown=True),
            rg.TextField(name="ai-message", use_markdown=True, required=False),
            rg.TextField(name="function-message", use_markdown=True, required=False),
            rg.TextField(name="system-message", use_markdown=True, required=False),
            rg.TextField(name="langsmith-url", use_markdown=True, required=False),
        ]

        questions = [
            rg.MultiLabelQuestion(
                name="issue",
                title="Please categorize the record:",
                labels=["follow-up needed", "reviewed", "no-repro", "not-helpful", "empty-response", "critical"],
            ),
            rg.TextQuestion(name="note", title="Leave a note to describe the issue:", required=False),
        ]

        metadata = [
            rg.TermsMetadataProperty(name="correctness-langsmith", values=df.correctness_langsmith.unique().tolist()),
            rg.TermsMetadataProperty(name="model-name", values=df.model_name.unique().tolist()),
            rg.FloatMetadataProperty(name="temperature", min=df.temperature.min(), max=df.temperature.max()),
            rg.IntegerMetadataFilter(name="max-tokens", min=df.max_tokens.min(), max=df.max_tokens.max()),
            rg.FloatMetadataProperty(name="cpu-user", min=df.cpu_time_user.min(), max=df.cpu_time_user.max()),
            rg.FloatMetadataProperty(name="cpu-system", min=df.cpu_time_system.min(), max=df.cpu_time_system.max()),
            rg.TermsMetadataProperty(name="library-version", values=df.library_version.unique().tolist()),
        ]

        dataset = rg.FeedbackDataset(fields=fields, questions=questions, metadata_properties=metadata)
        dataset.add_records(records=[LoadDatasets.build_error_analysis_record(row) for _, row in df.iterrows()])
        dataset.push_to_argilla(name="error-analysis-with-feedback-alpha", workspace="admin")

    @staticmethod
    def load_error_analysis_textcat_version():
        print("Loading Error Analysis dataset as a `DatasetForTextClassification`")
        df = pd.read_csv(
            "https://raw.githubusercontent.com/argilla-io/dataset_examples/main/synthetic_data_v2_with_vectors.csv"
        )

        labels = ["follow-up needed", "reviewed", "no-repro", "not-helpful", "empty-response", "critical"]
        settings = rg.TextClassificationSettings(label_schema=labels)
        rg.configure_dataset_settings(name="error-analysis-with-text-classification", settings=settings)

        records = [LoadDatasets.build_error_analysis_record(row, legacy=True) for _, row in df.iterrows()]
        rg.log(name="error-analysis-with-text-classification", records=records, batch_size=25)


if __name__ == "__main__":
    API_KEY = sys.argv[1]
    LOAD_DATASETS = sys.argv[2]

    if LOAD_DATASETS.lower() == "none":
        print("No datasets will be loaded")
    else:
        load_datasets = LOAD_DATASETS.lower().strip()
        while True:
            try:
                response = requests.get("http://0.0.0.0:6900/")
                if response.status_code == 200:
                    ld = LoadDatasets(API_KEY)
                    # TODO(@frascuchon): Remove these datasets creation
                    ld.load_error_analysis()
                    ld.load_error_analysis_textcat_version()
                    # END
                    ld.load_feedback_dataset_from_huggingface(
                        repo_id="argilla/databricks-dolly-15k-curated-en",
                        split="train",
                        samples=100,
                    )

                    if LOAD_DATASETS.lower() != "single":
                        # `Text2TextDataset``
                        ld.load_news_text_summarization()
                        # `TextClassificationDataset`
                        ld.load_news_programmatic_labeling()
                        ld.load_sst_sentiment_explainability()
                        # `TokenClassificationDataset`
                        ld.load_gutenberg_spacy_ner_monitoring()
                        # `FeedbackDataset`
                        ld.load_feedback_dataset_from_huggingface(
                            repo_id="argilla/oasst_response_quality",
                            split="train",
                            samples=100,
                        )
                        ld.load_feedback_dataset_from_huggingface(
                            repo_id="argilla/oasst_response_comparison",
                            split="train",
                            samples=100,
                        )
            except requests.exceptions.ConnectionError:
                pass
            except Exception as e:
                print(e)
                time.sleep(10)
                pass

            time.sleep(5)
