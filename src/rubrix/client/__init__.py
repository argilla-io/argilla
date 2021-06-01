# -*- coding: utf-8 -*-

"""Rubrix Client Init Method

Methods for using the Rubrix Client, called from the module init file.
"""

import logging
from typing import Any, Dict, Iterable, List, Optional, Union

import httpx
import pandas
from rubrix.client.models import (
    BulkResponse,
    DatasetSnapshot,
    Record,
    TextClassificationRecord,
    TokenAttributions,
    TokenClassificationRecord,
)
from rubrix.sdk import AuthenticatedClient, Client, models
from rubrix.sdk.api.datasets import delete_dataset
from rubrix.sdk.api.snapshots import list_dataset_snapshots
from rubrix.sdk.api.text_classification import bulk_records as text_classification_bulk
from rubrix.sdk.api.token_classification import (
    bulk_records as token_classification_bulk,
)
from rubrix.sdk.api.users import whoami
from rubrix.sdk.models import (
    TaskType,
    TextClassificationQuery,
    TokenClassificationQuery,
)
from rubrix.sdk.types import Response


class RubrixClient:
    """Class definition for Rubrix Client"""

    _LOGGER = logging.getLogger(__name__)  # _LOGGER intialization

    MAX_CHUNK_SIZE = 5000  # Larger sizzes will trigger a warning

    def __init__(
        self,
        api_url: str,
        timeout: int,
        api_key: Optional[str] = None,
    ):
        """Client setup function.

        Parameters
        ----------
        api_url : str
            Address from which the API is serving. It will use the default UVICORN address as default
        api_key : str
            Authentification token. A non-secured logging will be considered the default case.
        timeout : int
            Seconds to considered a connection timeout. Optional
        """

        self._client = None  # Variable to store the client after the init

        try:
            response = httpx.get(url=f"{api_url}/api/docs/spec.json").status_code
        except ConnectionRefusedError:
            raise Exception("Connection Refused: cannot connect to the API.")

        if response != 200:  # Incorrect authentication
            # default
            raise Exception("Unidentified error, it should not get here.")

        # Non-token case
        if api_key is None:
            self._client = Client(base_url=api_url, timeout=timeout)

        # Token case
        else:
            self._client = AuthenticatedClient(
                base_url=api_url, token=api_key, timeout=timeout
            )

            whoami_response_status = whoami.sync_detailed(client=self._client).status_code
            if whoami_response_status == 401:
                raise Exception("Authentification error: invalid credentials.")

    def log(
        self,
        records: Iterable[Record],
        name: str,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 500,
    ) -> BulkResponse:
        """
        Register a set of logs into Rubrix

        Parameters
        ----------
        records:
            The data records list.
        name:
            The dataset name
        tags:
            A set of tags related to dataset. Optional
        metadata:
            A set of extra info for dataset. Optional
        chunk_size:
            The default chunk size for data bulk

        Returns
        -------
        BulkResponse
            If successful, with a summary response from the API.

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

        # Divided into Text and Token Classification Bulks
        if record_type is TextClassificationRecord:
            bulk_class = models.TextClassificationBulkData
            bulk_records_function = text_classification_bulk.sync_detailed
            tags = models.TextClassificationBulkDataTags.from_dict(tags)
            metadata = models.TextClassificationBulkDataMetadata.from_dict(metadata)
            to_sdk_model = self._text_classification_record_to_sdk

        elif record_type is TokenClassificationRecord:
            bulk_class = models.TokenClassificationBulkData
            bulk_records_function = token_classification_bulk.sync_detailed
            tags = models.TokenClassificationBulkDataTags.from_dict(tags)
            metadata = models.TokenClassificationBulkDataMetadata.from_dict(metadata)
            to_sdk_model = self._token_classification_record_to_sdk

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
        snapshot: Optional[str] = None,
        ids: Optional[List[Union[str, int]]] = None,
        limit: Optional[int] = None,
    ) -> pandas.DataFrame:

        if snapshot:
            from rubrix.sdk.api.snapshots import _get_data

            response = _get_data.sync_detailed(
                client=self._client, name=name, snapshot_id=snapshot, limit=limit
            )
            _check_response_errors(response)
            return pandas.DataFrame(response.parsed)
        else:

            from rubrix.sdk.api.datasets import get_dataset

            response = get_dataset.sync_detailed(client=self._client, name=name)
            _check_response_errors(response)
            task = response.parsed.task

            if task == TaskType.TEXTCLASSIFICATION:
                from rubrix.sdk.api.text_classification import _get_dataset_data

                map_fn = self._text_classification_sdk_to_record
                request_class = TextClassificationQuery
            elif task == TaskType.TOKENCLASSIFICATION:
                from rubrix.sdk.api.token_classification import _get_dataset_data

                map_fn = self._token_classification_sdk_to_record
                request_class = TokenClassificationQuery
            else:
                raise ValueError(
                    f"Sorry, load method is only allowed with token and text classification"
                )
            response = _get_dataset_data.sync_detailed(
                client=self._client,
                name=name,
                request=request_class(ids=ids or []),
                limit=limit,
            )

            return pandas.DataFrame(
                map(lambda r: r.dict(), map(map_fn, response.parsed))
            )

    def snapshots(self, dataset: str) -> List[DatasetSnapshot]:
        """
        Retrieves created snapshots for given dataset

        Parameters
        ----------
        dataset: str
            The dataset name

        Returns
        -------
            A list of snapshots

        """

        response = list_dataset_snapshots.sync_detailed(
            client=self._client, name=dataset
        )
        _check_response_errors(response)

        return [
            DatasetSnapshot(
                id=snapshot.id, task=snapshot.task, creation_date=snapshot.creation_date
            )
            for snapshot in response.parsed
        ]

    @staticmethod
    def _text_classification_sdk_to_record(
        sdk: Union[models.TextClassificationRecord, Dict[str, Any]]
    ) -> TextClassificationRecord:
        """Transforms and returns the sdk model as a `TextClassificationRecord` record"""
        if isinstance(sdk, models.TextClassificationRecord):
            sdk = sdk.to_dict()

        record = TextClassificationRecord(
            id=sdk.get("id"),
            event_timestamp=sdk.get("event_timestamp"),
            inputs=sdk.get("text", sdk.get("inputs")),
            multi_label=sdk.get("multi_label"),
            status=sdk.get("status"),
        )

        prediction = sdk.get("prediction")
        if prediction:
            record.prediction = [
                (label["class"], label["confidence"]) for label in prediction["labels"]
            ]
            record.prediction_agent = prediction["agent"]

        annotation = sdk.get("annotation")
        if annotation:
            # TODO(dfidalgo): it's depends on multilabel field?
            record.annotation = [label["class"] for label in annotation["labels"]]
            record.annotation_agent = annotation["agent"]

        explanation = sdk.get("explanation")
        if explanation:
            record.explanation = {
                key: [TokenAttributions(**attribution) for attribution in attributions]
                for key, attributions in explanation
            }
        metadata = sdk.get("metadata")
        if metadata:
            record.metadata = metadata

        return record

    @staticmethod
    def _text_classification_record_to_sdk(
        record: TextClassificationRecord,
    ) -> models.TextClassificationRecord:
        """Transforms and returns the record as an SDK `TextClassificationRecord` model"""
        model_dict = {
            "inputs": record.inputs,
            "multi_label": record.multi_label,
            "status": record.status,
        }
        if record.prediction is not None:
            labels = [
                {"class": label, "confidence": confidence}
                for label, confidence in record.prediction
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
            gold_labels = [{"class": label, "confidence": 1.0} for label in annotations]
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

    def delete(self, name: str):
        """
        Delete a dataset with given name

        Parameters
        ----------
        name:
            The dataset name
        """
        response = delete_dataset.sync_detailed(client=self._client, name=name)
        _check_response_errors(response)

    @staticmethod
    def _token_classification_sdk_to_record(
        sdk: Union[models.TokenClassificationRecord, Dict[str, Any]]
    ) -> TokenClassificationRecord:
        if isinstance(sdk, models.TokenClassificationRecord):
            sdk = sdk.to_dict()
        record = TokenClassificationRecord(
            id=sdk.get("id"),
            event_timestamp=sdk.get("event_timestamp"),
            tokens=sdk.get("tokens"),
            text=sdk.get("raw_text"),
            status=sdk.get("status"),
        )

        prediction = sdk.get("prediction")
        if prediction:
            record.prediction_agent = prediction["agent"]
            record.prediction = [
                (entity["label"], entity["start"], entity["end"])
                for entity in prediction["entities"]
            ]

        annotation = sdk.get("annotation")
        if annotation:
            record.annotation = [
                (entity["label"], entity["start"], entity["end"])
                for entity in annotation["entities"]
            ]
            record.annotation_agent = annotation["agent"]

        metadata = sdk.get("metadata")
        if metadata:
            record.metadata = metadata

        return record

    @staticmethod
    def _token_classification_record_to_sdk(record: TokenClassificationRecord):
        """Transforms and returns the record as an SDK `TokenClassificationRecord` model"""
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
