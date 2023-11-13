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

# %%
import re
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
from tqdm import tqdm
import textdescriptives as td

from argilla.client.feedback.dataset.local.dataset import FeedbackDataset
from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset
from argilla.client.feedback.schemas.metadata import (
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
)
from argilla.client.feedback.schemas.records import FeedbackRecord
from argilla.client.feedback.schemas.remote.records import RemoteFeedbackRecord


# %%
class TextDescriptivesExtractor:
    """This class extracts a number of basic text descriptives from FeedbackDataset
    records using the TextDescriptives library and adds them as record metadata."""

    def __init__(
        self,
        model: str = "en",
        metrics: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
        visible_for_annotators: bool = True,
        progress: bool = True,
    ):
        """
        Initialize a new TextDescriptivesExtractor object.

        Args:
            model (str): The language model to use for text descriptives.
            metrics (Optional[List[str]]): A list of metrics to extract. If None, all metrics will be extracted.
            fields (Optional[List[str]]): A list of field names to extract metrics from. If None, all fields will be used.
            visible_for_annotators (bool): Whether the extracted metrics should be visible to annotators.
            progress (bool): Whether to show a progress bar when extracting metrics.
        """
        self.model = model
        self.metrics = metrics
        self.fields = fields
        self.visible_for_annotators = visible_for_annotators
        self.progress = progress
        self.__basic_metrics = [
            "n_tokens",
            "n_unique_tokens",
            "n_sentences",
            "perplexity",
            "entropy",
            "flesch_reading_ease",
        ]

    def _extract_metrics_for_single_field(
        self,
        records: List[Union[FeedbackRecord, RemoteFeedbackRecord]],
        field: str,
        basic_metrics: Optional[List[str]] = None,
    ) -> Optional[pd.DataFrame]:
        """
        Extract text descriptives metrics for a single field from a list of feedback records
        using the TextDescriptives library.

        Args:
            records (List[Union[FeedbackRecord, RemoteFeedbackRecord]]): A list of FeedbackDataset or RemoteFeedbackDataset records.
            field (str): The name of the field to extract metrics for.
            basic_metrics (Optional[List[str]]): A list of basic metrics to extract. If None, all metrics will be extracted.

        Returns:
            Optional[pd.DataFrame]: A dataframe containing the text descriptives metrics for the field, or None if the field is empty.
        """
        # If the field is empty, skip it
        if not any(record.fields[field] for record in records):
            return None
        field_text = [record.fields[field] for record in records]
        field_metrics = td.extract_metrics(text=field_text, lang=self.model, metrics=self.metrics)
        # Drop any column containing NaNs
        field_metrics = field_metrics.dropna(axis=1, how="any")
        # If basic metrics is None, use all basic metrics
        if basic_metrics is None and self.metrics is None:
            basic_metrics = self.__basic_metrics 
            field_metrics = field_metrics.loc[:, basic_metrics]
        
        # Concatenate field name with the metric name
        field_metrics.columns = [f"{field}_{metric}" for metric in field_metrics.columns]
        return field_metrics

    def _extract_metrics_for_all_fields(
        self, records: List[Union[FeedbackRecord, RemoteFeedbackRecord]], fields: Optional[Union[str, List[str]]] = None
    ) -> pd.DataFrame:
        """
        Extract text descriptives metrics for all named fields from a list of feedback records
        using the TextDescriptives library.
        Args:
            records (List[Union[FeedbackRecord, RemoteFeedbackRecord]]): A list of FeedbackDataset or RemoteFeedbackDataset records.
            fields (Optional[Union[str, List[str]]]): A list of fields to extract metrics for. If None, extract metrics for all fields.
        Returns:
            pd.DataFrame: A dataframe containing the text descriptives metrics for each record and field.
        """
        # If fields is None, use all fields
        if fields is None:
            # Programmatically select all fields in the records
            fields = list({key for record in records for key in record.fields.keys()})
        # Extract all metrics for each field
        field_metrics = {
            field: self._extract_metrics_for_single_field(records=records, field=field) for field in fields
        }
        field_metrics = {field: metrics for field, metrics in field_metrics.items() if metrics is not None}
        # If there is only one field, return the metrics for that field directly
        if len(field_metrics) == 1:
            return list(field_metrics.values())[0]
        # If there are multiple fields, combine metrics for each field into a single dataframe
        final_metrics = pd.concat(field_metrics, axis=1, keys=field_metrics.keys())
        return final_metrics

    def _clean_column_name(self, col_name: str) -> str:
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

    def _cast_to_python_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert integer, boolean and floats columns in a dataframe
        to Python native types.

        Args:
            df (pd.DataFrame): The text descriptives dataframe.

        Returns:
            pd.DataFrame: The text descriptives dataframe with integer and boolean columns cast to Python native types.
        """
        # Select columns by data type
        int_cols = df.select_dtypes(include=["int64"]).columns
        bool_cols = df.select_dtypes(include=["boolean"]).columns
        float_cols = df.select_dtypes(include=["float64"]).columns
        # Cast integer columns to Python's native int type
        df[int_cols] = df[int_cols].astype(int)
        # Cast boolean columns to Python's native str type
        df[bool_cols] = df[bool_cols].astype(str)
        # Cast float columns to Python's native float type and round to 2 decimal places
        df[float_cols] = df[float_cols].astype(float).round(2)
        return df

    def _create_metadata_properties(self, df: pd.DataFrame) -> List:
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
            name = f"{self._clean_column_name(col)}"
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

    def _add_text_descriptives_to_metadata(
        self, records: List[Union[FeedbackRecord, RemoteFeedbackRecord]], df: pd.DataFrame
    ) -> List[Union[FeedbackRecord, RemoteFeedbackRecord]]:
        """
        Add the text descriptives metrics extracted previously as metadata
        to a list of FeedbackDataset records.

        Args:
            records (List[Union[FeedbackRecord, RemoteFeedbackRecord]]): A list of FeedbackDataset or RemoteFeedbackDataset records.
            df (pd.DataFrame): The text descriptives dataframe.

        Returns:
            List[Union[FeedbackRecord, RemoteFeedbackRecord]]: A list of FeedbackDataset or RemoteFeedbackDataset records with extracted metrics added as metadata.
        """
        # Loop through the records and add the metrics to the metadata
        modified_records = []
        # Make tqdm optional
        for record, metrics in tqdm(
            zip(records, df.to_dict("records")),
            total=len(records),
            disable=not self.progress,
            desc="Getting text descriptives...",
        ):
            record.metadata.update(metrics)
            modified_records.append(record)
        return modified_records

    def update_dataset(
        self, dataset: Union[FeedbackDataset, RemoteFeedbackDataset]
    ) -> Union[FeedbackDataset, RemoteFeedbackDataset]:
        """
        Extract text descriptives metrics from a records in a FeedbackDataset
        or RemoteFeedbackDataset, add them as metadata to the records and
        return the updated dataset.

        Args:
            dataset (Union[FeedbackDataset, RemoteFeedbackDataset]): A FeedbackDataset or RemoteFeedbackDataset.

        Returns:
            Union[FeedbackDataset, RemoteFeedbackDataset]: A FeedbackDataset or RemoteFeedbackDataset with text descriptives metrics added as metadata.
        """
        # Extract records
        records = dataset.records
        # Extract text descriptives metrics from records
        extracted_metrics = self._extract_metrics_for_all_fields(records)
        # Cast integer and boolean columns to Python native types
        extracted_metrics = self._cast_to_python_types(extracted_metrics)
        # Create metadata properties based on dataframe columns and data types
        metadata_properties = self._create_metadata_properties(extracted_metrics)
        # Add each metadata property iteratively to the dataset
        [dataset.add_metadata_property(prop) for prop in metadata_properties]
        # Add the metrics to the metadata of the records
        modified_records = self._add_text_descriptives_to_metadata(records, extracted_metrics)
        # Add the modified records to the local dataset
        dataset.update_records(modified_records)
        return dataset