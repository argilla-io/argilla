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

"""Rubrix Client Init Method

Methods for using the Rubrix Client, called from the module init file.
"""

import logging
from typing import Any, Dict, Iterable, List, Optional, Union

import httpx
import pandas
from rubrix.client.models import (
    BulkResponse,
    Record,
    TextClassificationRecord,
    TokenAttributions,
    TokenClassificationRecord,
    Text2TextRecord,
)
from rubrix.sdk import AuthenticatedClient, models
from rubrix.sdk.models.text2_text_record import Text2TextRecord as Text2TextRecordSdk
from rubrix.sdk.models.text2_text_bulk_data import Text2TextBulkData
from rubrix.sdk.models.text2_text_bulk_data_metadata import Text2TextBulkDataMetadata
from rubrix.sdk.models.text2_text_bulk_data_tags import Text2TextBulkDataTags
from rubrix.sdk.models.text2_text_query import Text2TextQuery
from rubrix.sdk.api.text2_text import bulk_records as text2text_bulk_records
from rubrix.sdk.api.datasets import copy_dataset, delete_dataset
from rubrix.sdk.api.text_classification import (
    bulk_records as text_classification_bulk_records,
)
from rubrix.sdk.api.token_classification import (
    bulk_records as token_classification_bulk_records,
)
from rubrix.sdk.api.users import whoami
from rubrix.sdk.models import (
    TaskType,
    TextClassificationQuery,
    TokenClassificationQuery,
)
from rubrix.sdk.models.copy_dataset_request import CopyDatasetRequest
from rubrix.sdk.types import Response
from rubrix.sdk.api.datasets import get_dataset
from rubrix.sdk.api.text_classification import (
    _get_dataset_data as text_classification_get_dataset_data,
)
from rubrix.sdk.api.token_classification import (
    _get_dataset_data as token_classification_get_dataset_data,
)
from rubrix.sdk.api.text2_text import (
    _get_dataset_data as text2text_get_dataset_data,
)


class RubrixClient:
    """Class definition for Rubrix Client"""

    _LOGGER = logging.getLogger(__name__)

    # Larger sizes will trigger a warning
    MAX_CHUNK_SIZE = 5000

    def __init__(
        self,
        api_url: str,
        api_key: str,
        timeout: int = 60,
    ):
        """Client setup function.

        Args:
            api_url:
                Address from which the API is serving.
            api_key:
                Authentication token.
            timeout:
                Seconds to considered a connection timeout.
        """

        self._client = None  # Variable to store the client after the init

        try:
            response = httpx.get(url=f"{api_url}/api/docs/spec.json")
        except ConnectionRefusedError:
            raise Exception("Connection Refused: cannot connect to the API.")

        if response.status_code != 200:
            raise Exception(
                "Connection error: Undetermined error connecting to the Rubrix Server. "
                "The API answered with a {} code: {}".format(
                    response.status_code, response.content
                )
            )
        self._client = AuthenticatedClient(
            base_url=api_url, token=api_key, timeout=timeout
        )

        whoami_response_status = whoami.sync_detailed(client=self._client).status_code
        if whoami_response_status == 401:
            raise Exception("Authentication error: invalid credentials.")

    def log(
        self,
        records: Iterable[Record],
        name: str,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 500,
    ) -> BulkResponse:
        """Log records to Rubrix.

        Args:
            records:
                The records to be logged.
            name:
                The dataset name.
            tags:
                A set of tags related to the dataset.
            metadata:
                A set of extra info for the dataset.
            chunk_size:
                Records are logged in chunks to the Rubrix server, this defines their sizes.

        Returns:
            A summary response from the API.

        """

        if not name:
            raise Exception("Empty project name has been passed as argument.")

        records = list(records)
        tags = tags or {}
        metadata = metadata or {}

        try:
            record_type = type(records[0])
        except IndexError:
            raise Exception("Empty record list has been passed as argument.")

        processed = 0
        failed = 0

        # Check chunk_size <= length of training dataset not needed, as the Python slice system will adjust
        # a bigger-than-possible length to the whole list, having all input in the same chunk.
        # However, a desired check can be placed to create a custom chunk_size when that limit is exceeded
        if chunk_size > self.MAX_CHUNK_SIZE:
            self._LOGGER.warning(
                """The introduced chunk size is noticeably large, timeout erros may ocurr.
                Consider a chunk size smaller than %s""",
                self.MAX_CHUNK_SIZE,
            )

        # Check record type
        if record_type is TextClassificationRecord:
            bulk_class = models.TextClassificationBulkData
            bulk_records_function = text_classification_bulk_records.sync_detailed
            tags = models.TextClassificationBulkDataTags.from_dict(tags)
            metadata = models.TextClassificationBulkDataMetadata.from_dict(metadata)
            to_sdk_model = self._text_classification_client_to_sdk

        elif record_type is TokenClassificationRecord:
            bulk_class = models.TokenClassificationBulkData
            bulk_records_function = token_classification_bulk_records.sync_detailed
            tags = models.TokenClassificationBulkDataTags.from_dict(tags)
            metadata = models.TokenClassificationBulkDataMetadata.from_dict(metadata)
            to_sdk_model = self._token_classification_client_to_sdk

        elif record_type is Text2TextRecord:
            bulk_class = Text2TextBulkData
            bulk_records_function = text2text_bulk_records.sync_detailed
            tags = Text2TextBulkDataTags.from_dict(tags)
            metadata = Text2TextBulkDataMetadata.from_dict(metadata)
            to_sdk_model = self._text2text_client_to_sdk

        # Record type is not recognised
        else:
            raise Exception(
                f"Unknown record type passed as argument for [{','.join(map(str, records[0:5]))}...] "
                f"Available values are {Record.__args__}"
            )

        for i in range(0, len(records), chunk_size):
            chunk = records[i : i + chunk_size]

            response = bulk_records_function(
                client=self._client,
                name=name,
                json_body=bulk_class(
                    tags=tags,
                    metadata=metadata,
                    records=[to_sdk_model(r) for r in chunk],
                ),
            )

            _check_response_errors(response)
            processed += response.parsed.processed
            failed += response.parsed.failed

        # Creating a composite BulkResponse with the total processed and failed
        return BulkResponse(dataset=name, processed=processed, failed=failed)

    def load(
        self,
        name: str,
        ids: Optional[List[Union[str, int]]] = None,
        limit: Optional[int] = None,
    ) -> pandas.DataFrame:
        """Load dataset data to a pandas DataFrame.

        Args:
            name:
                The dataset name.
            ids:
                If provided, load dataset records with given ids.
            limit:
                The number of records to retrieve.

        Returns:
            The dataset as a pandas Dataframe.
        """
        response = get_dataset.sync_detailed(client=self._client, name=name)
        _check_response_errors(response)
        task = response.parsed.task

        task_config = {
            TaskType.TEXTCLASSIFICATION: (
                text_classification_get_dataset_data,
                self._text_classification_sdk_to_client,
                TextClassificationQuery,
            ),
            TaskType.TOKENCLASSIFICATION: (
                token_classification_get_dataset_data,
                self._token_classification_sdk_to_client,
                TokenClassificationQuery,
            ),
            TaskType.TEXT2TEXT: (
                text2text_get_dataset_data,
                self._text2text_sdk_to_client,
                Text2TextQuery,
            ),
        }

        try:
            get_dataset_data, map_fn, request_class = task_config[task]
        except KeyError:
            raise ValueError(
                f"Sorry, load method not supported for the '{task}' task. Supported tasks: "
                f"{[TaskType.TEXTCLASSIFICATION, TaskType.TOKENCLASSIFICATION, TaskType.TEXT2TEXT]}"
            )
        response = get_dataset_data.sync_detailed(
            client=self._client,
            name=name,
            request=request_class(ids=ids or []),
            limit=limit,
        )

        return pandas.DataFrame(map(lambda r: r.dict(), map(map_fn, response.parsed)))

    @staticmethod
    def _text_classification_sdk_to_client(
        record: Union[models.TextClassificationRecord, Dict[str, Any]]
    ) -> TextClassificationRecord:
        """Returns the client model of the record given its sdk model"""
        if isinstance(record, models.TextClassificationRecord):
            record = record.to_dict()

        annotations = (
            [label["class"] for label in record["annotation"]["labels"]]
            if record.get("annotation")
            else None
        )
        if annotations and not record["multi_label"]:
            annotations = annotations[0]

        return TextClassificationRecord(
            id=record.get("id"),
            event_timestamp=record.get("event_timestamp"),
            inputs=record.get("text", record.get("inputs")),
            multi_label=record["multi_label"],
            status=record.get("status"),
            metadata=record.get("metadata") or {},
            prediction=[
                (label["class"], label["score"])
                for label in record["prediction"]["labels"]
            ]
            if record.get("prediction")
            else None,
            prediction_agent=record["prediction"].get("agent")
            if record.get("prediction")
            else None,
            annotation=annotations,
            annotation_agent=record["annotation"].get("agent")
            if record.get("annotation")
            else None,
            explanation={
                key: [TokenAttributions(**attribution) for attribution in attributions]
                for key, attributions in record["explanation"].items()
            }
            if record.get("explanation")
            else None,
        )

    @staticmethod
    def _text_classification_client_to_sdk(
        record: TextClassificationRecord,
    ) -> models.TextClassificationRecord:
        """Returns the sdk model of the record given its client model"""
        model_dict = {
            "inputs": record.inputs,
            "multi_label": record.multi_label,
            "status": record.status,
        }
        if record.prediction is not None:
            labels = [
                {"class": label, "score": score}
                for label, score in record.prediction
            ]
            model_dict["prediction"] = {
                "agent": record.prediction_agent or "None",
                "labels": labels,
            }
        if record.annotation is not None:
            annotations = (
                record.annotation
                if isinstance(record.annotation, list)
                else [record.annotation]
            )
            gold_labels = [{"class": label, "score": 1.0} for label in annotations]
            model_dict["annotation"] = {
                "agent": record.annotation_agent or "None",
                "labels": gold_labels,
            }
            model_dict["status"] = record.status or "Validated"
        if record.explanation is not None:
            model_dict["explanation"] = {
                key: [attribution.dict() for attribution in value]
                for key, value in record.explanation.items()
            }
        if record.id is not None:
            model_dict["id"] = record.id
        if record.metadata is not None:
            model_dict["metadata"] = record.metadata
        if record.event_timestamp is not None:
            model_dict["event_timestamp"] = record.event_timestamp.isoformat()

        return models.TextClassificationRecord.from_dict(model_dict)

    @staticmethod
    def _token_classification_sdk_to_client(
        record: Union[models.TokenClassificationRecord, Dict[str, Any]]
    ) -> TokenClassificationRecord:
        """Returns the client model of the record given its sdk model"""
        if isinstance(record, models.TokenClassificationRecord):
            record = record.to_dict()

        return TokenClassificationRecord(
            id=record.get("id"),
            event_timestamp=record.get("event_timestamp"),
            tokens=record.get("tokens"),
            text=record.get("raw_text"),
            status=record.get("status"),
            metadata=record.get("metadata") or {},
            prediction=[
                (entity["label"], entity["start"], entity["end"])
                for entity in record["prediction"]["entities"]
            ]
            if record.get("prediction")
            else None,
            prediction_agent=record["prediction"].get("agent")
            if record.get("prediction")
            else None,
            annotation=[
                (entity["label"], entity["start"], entity["end"])
                for entity in record["annotation"]["entities"]
            ]
            if record.get("annotation")
            else None,
            annotation_agent=record["annotation"].get("agent")
            if record.get("annotation")
            else None,
        )

    @staticmethod
    def _token_classification_client_to_sdk(
        record: TokenClassificationRecord,
    ) -> models.TokenClassificationRecord:
        """Returns the sdk model of the record given its client model"""
        model_dict = {
            "raw_text": record.text,
            "tokens": record.tokens,
            "status": record.status,
        }
        if record.prediction is not None:
            entities = [
                {"label": pred[0], "start": pred[1], "end": pred[2]}
                for pred in record.prediction
            ]
            model_dict["prediction"] = {
                "agent": record.prediction_agent,
                "entities": entities,
            }
        if record.annotation is not None:
            gold_entities = [
                {"label": ann[0], "start": ann[1], "end": ann[2]}
                for ann in record.annotation
            ]
            model_dict["annotation"] = {
                "agent": record.annotation_agent,
                "entities": gold_entities,
            }
        if record.id is not None:
            model_dict["id"] = record.id
        if record.metadata is not None:
            model_dict["metadata"] = record.metadata
        if record.event_timestamp is not None:
            model_dict["event_timestamp"] = record.event_timestamp.isoformat()

        return models.TokenClassificationRecord.from_dict(model_dict)

    @staticmethod
    def _text2text_sdk_to_client(
        record: Union[Text2TextRecordSdk, Dict[str, Any]]
    ) -> Text2TextRecord:
        """Returns the client model of the record given its sdk model"""
        if isinstance(record, Text2TextRecordSdk):
            record = record.to_dict()

        return Text2TextRecord(
            text=record.get("text"),
            id=record.get("id"),
            event_timestamp=record.get("event_timestamp"),
            status=record.get("status"),
            metadata=record.get("metadata") or {},
            prediction=[
                (pred["text"], pred.get("score"))
                for pred in record["prediction"]["sentences"]
            ]
            if record.get("prediction")
            else None,
            prediction_agent=record["prediction"].get("agent")
            if record.get("prediction")
            else None,
            annotation=record["annotation"]["sentences"][0]["text"]
            if record.get("annotation")
            else None,
            annotation_agent=record["annotation"].get("agent")
            if record.get("annotation")
            else None,
        )

    @staticmethod
    def _text2text_client_to_sdk(record: Text2TextRecord) -> Text2TextRecordSdk:
        """Returns the sdk model of the record given its client model"""
        model_dict = {
            "text": record.text,
            "status": record.status,
        }
        if record.prediction is not None:
            sentences = [
                {"text": text, "score": score} for text, score in record.prediction
            ]
            model_dict["prediction"] = {
                "agent": record.prediction_agent or "None",
                "sentences": sentences,
            }
        if record.annotation is not None:
            sentence = {"text": record.annotation, "score": 1.0}
            model_dict["annotation"] = {
                "agent": record.annotation_agent or "None",
                "sentences": [sentence],
            }

        if record.id is not None:
            model_dict["id"] = record.id
        if record.metadata is not None:
            model_dict["metadata"] = record.metadata
        if record.event_timestamp is not None:
            model_dict["event_timestamp"] = record.event_timestamp.isoformat()

        return Text2TextRecordSdk.from_dict(model_dict)

    def copy(self, source: str, target: str):
        """Makes a copy of the `source` dataset and saves it as `target`"""
        response = copy_dataset.sync_detailed(
            client=self._client, name=source, json_body=CopyDatasetRequest(name=target)
        )
        if response.status_code == 409:
            raise RuntimeError(f"A dataset with name '{target}' already exists.")

    def delete(self, name: str):
        """Delete a dataset with given name

        Args:
            name:
                The dataset name
        """
        response = delete_dataset.sync_detailed(client=self._client, name=name)
        _check_response_errors(response)


def _check_response_errors(response: Response) -> None:
    """Checks response status codes and raise corresponding error if found"""

    http_status = response.status_code
    response_data = response.parsed

    if http_status == 401:
        raise Exception(
            "Unauthorized error: invalid credentials. The API answered with a {} code: {}".format(
                http_status, response_data
            )
        )

    elif http_status == 403:
        raise Exception(
            "Forbidden error: you have not been authorised to access this dataset. "
            "The API answered with a {} code: {}".format(http_status, response_data)
        )

    elif http_status == 404:
        raise Exception(
            "Not found error. The API answered with a {} code: {}".format(
                http_status, response_data
            )
        )

    elif http_status == 422:
        raise Exception(
            "Unprocessable entity error: Something is wrong in your records. "
            "The API answered with a {} code: {}".format(http_status, response_data)
        )

    elif 400 <= http_status < 500:
        raise Exception(
            "Request error: API cannot answer. "
            "The API answered with a {} code: {}".format(http_status, response_data)
        )

    elif http_status >= 500:
        raise Exception(
            "Connection error: API is not responding. "
            "The API answered with a {} code: {}".format(http_status, response_data)
        )
