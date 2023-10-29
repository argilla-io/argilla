#  coding=utf-8
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

import re
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
import textdescriptives as td
from tqdm import tqdm

from argilla.client.feedback.dataset.local.dataset import FeedbackDataset
from argilla.client.feedback.schemas.metadata import (
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
)
from argilla.client.feedback.schemas.records import FeedbackRecord


class TextDescriptivesExtractor:
    """This class extracts a number of basic text descriptives from FeedbackDataset
    records using the TextDescriptives library and adds them as record metadata."""

    def __init__(
        self,
        model: str = "en",
        metrics: list[str] = ["quality", "readability", "information_theory"],
        visible_for_annotators: bool = True,
        fields: Optional[List[str]] = None,
    ):
        """
        Initialize a new TextDescriptivesExtractor object.

        Args:
            model (str): The language model to use for text descriptives.
            metrics (list[str]): The list of metrics to extract.
            visible_for_annotators (bool): Whether the extracted metrics should be visible to annotators.
            fields (Optional[List[str]]): A list of field names to extract metrics from. If None, defaults to ["text"].
        """
        self.model = model
        self.metrics = metrics
        self.visible_for_annotators = visible_for_annotators
        self.fields = fields or ["text"]

    def extract_metrics(self, records: List[FeedbackRecord]) -> pd.DataFrame:
        """
        Extract text descriptives metrics for multiple fields from a list of feedback records
        using the TextDescriptives library.

        Args:
            records (List[FeedbackRecord]): A list of FeedbackDataset records.

        Returns:
            pd.DataFrame: A dataframe containing the text descriptives metrics for each record and field.
        """
        # Define a list of basic metrics to keep
        metrics_to_keep = [
            "n_tokens",
            "n_unique_tokens",
            "n_sentences",
            "perplexity",
            "entropy",
            "flesch_reading_ease",
            # "smog",
        ]
        field_metrics = {}
        # For each field, extract the metrics from the corresponding field in each record
        for field in self.fields:
            field_text = [record.fields[field] for record in records]
            field_metrics[field] = td.extract_metrics(text=field_text, lang=self.model, metrics=self.metrics)
            field_metrics[field] = field_metrics[field].loc[:, metrics_to_keep]
        # Combine metrics for each field into a single dataframe
        combined_metrics = pd.concat(field_metrics, axis=1, keys=field_metrics.keys())
        # Flatten multi-index columns and concatenate field name with the metric name
        combined_metrics.columns = [f"{field}_{metric}" for field, metric in combined_metrics.columns]
        return combined_metrics

    def clean_column_name(self, col_name: str) -> str:
        """
        Clean the column name of a dataframe to fit a specific regex pattern.

        Args:
            col_name (str): A column name.

        Returns:
            str: A column name that fits the regex pattern.
        """
        col_name = col_name.lower()  # Convert to lowercase
        col_name = re.sub(r"[^a-z0-9_]", "_", col_name)  # Replace non-alphanumeric characters with underscores
        return col_name

    def cast_to_python_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert integer, boolean and floats columns in a dataframe
        to Python native types.

        Args:
            df (pd.DataFrame): The text descriptives dataframe.

        Returns:
            pd.DataFrame: The text descriptives dataframe with integer and boolean columns cast to Python native types.
        """
        int_cols = df.select_dtypes(include=["int64"]).columns
        bool_cols = df.select_dtypes(include=["boolean"]).columns
        float_cols = df.select_dtypes(include=["float64"]).columns
        # Explicitly cast integers using Python's native int type
        for col in int_cols:
            df[col] = df[col].apply(int)
        # Convert booleans to strings using Python's native str type
        for col in bool_cols:
            df[col] = df[col].apply(str)
        # Explicitly cast floats using Python's native float type and round to 2 decimal places
        for col in float_cols:
            df[col] = df[col].apply(lambda x: round(float(x), 2))
        return df

    def create_metadata_properties(self, df: pd.DataFrame) -> List:
        """
        Generate metadata properties based on dataframe columns and data types.

        Args:
            df (pd.DataFrame): The text descriptives dataframe.

        Returns:
            List: A list of metadata properties.
        """
        ### TO DO: Handle nans
        properties = []
        for col, dtype in df.dtypes.items():
            name = f"{self.clean_column_name(col)}"
            title = name.replace("_", " ").title()
            if dtype == "object":
                prop = TermsMetadataProperty(name=name, title=title, visible_for_annotators=self.visible_for_annotators)
            elif dtype == "int64":
                prop = IntegerMetadataProperty(
                    name=name, title=title, visible_for_annotators=self.visible_for_annotators
                )
            elif dtype == "float64":
                prop = FloatMetadataProperty(name=name, title=title, visible_for_annotators=self.visible_for_annotators)
            elif dtype == "bool":
                prop = TermsMetadataProperty(name=name, title=title, visible_for_annotators=self.visible_for_annotators)
            else:
                print(f"Unhandled data type for column {col}: {dtype}")
                continue
            properties.append(prop)
        return properties

    def add_text_descriptives_to_metadata(
        self, records: List[FeedbackRecord], df: pd.DataFrame
    ) -> List[FeedbackRecord]:
        """
        Add the text descriptives metrics extracted previously as metadata
        to a list of FeedbackDataset records.

        Args:
            records (List[FeedbackRecord]): A list of FeedbackDataset records.
            df (pd.DataFrame): The text descriptives dataframe.

        Returns:
            List[FeedbackRecord]: A list of FeedbackDataset records with updated metadata.
        """
        # Loop through the records and add the metrics to the metadata
        modified_records = []
        for record, metrics in tqdm(zip(records, df.to_dict("records")), total=len(records)):
            record.metadata.update(metrics)
            modified_records.append(record)
        return modified_records

    # def update_records(self, records: List[FeedbackRecord]) -> List[FeedbackRecord]:
    #     """Updates the metadata of a list of feedback records with text descriptives metrics
    #     and returns a list of updated feedback records.
    #     """
    #     # Create a dataset from the records

    #     # Extract the metrics
    #     extracted_metrics = self.extract_metrics(records)
    #     # Create metadata properties based on dataframe columns and data types
    #     metadata_properties = self.create_metadata_properties(extracted_metrics, prefix="text_descriptives")
    #     # Add the metrics to the metadata of the records
    #     modified_records = self.add_text_descriptives_to_metadata(records, extracted_metrics)
    #     return modified_records

    def update_dataset(self, dataset: FeedbackDataset) -> FeedbackDataset:
        """
        Take a FeedbackDataset and add text descriptives metrics for all of its
        records as record metadata.

        Args:
            dataset (FeedbackDataset): A FeedbackDataset.

        Returns:
            FeedbackDataset: A FeedbackDataset with updated metadata.
        """
        # Extract records
        records = dataset.records
        # Extract text descriptives metrics from records
        extracted_metrics = self.extract_metrics(records)
        # Cast integer and boolean columns to Python native types
        extracted_metrics = self.cast_to_python_types(extracted_metrics)
        # Create metadata properties based on dataframe columns and data types
        metadata_properties = self.create_metadata_properties(extracted_metrics)
        # Create a local dataset
        local_dataset = FeedbackDataset(
            guidelines=dataset.guidelines,
            fields=dataset.fields,
            questions=dataset.questions,
            metadata_properties=metadata_properties,
        )
        # Add the metrics to the metadata of the records
        modified_records = self.add_text_descriptives_to_metadata(records, extracted_metrics)
        # Add the modified records to the local dataset
        local_dataset.add_records(modified_records)
        return local_dataset
