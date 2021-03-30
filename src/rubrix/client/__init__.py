# -*- coding: utf-8 -*-

"""Rubrix Client Init Method

Methods for using the Rubrix Client, called from the module init file.
"""


import logging
from typing import Any, Dict, Iterable, List, Optional

import requests
from rubrix.client import models
from rubrix.client.models import (
    BulkResponse,
    DatasetSnapshot,
    TextClassificationRecord,
    TokenClassificationRecord,
)
from rubrix.sdk import AuthenticatedClient, Client
from rubrix.sdk.api.snapshots import list_dataset_snapshots
from rubrix.sdk.api.text_classification import bulk_records as text_classification_bulk
from rubrix.sdk.api.token_classification import (
    bulk_records as token_classification_bulk,
)
from rubrix.sdk import models
from rubrix.sdk.types import Response


class RubrixClient:
    """Class definition for Rubrix Client"""

    _LOGGER = logging.getLogger(__name__)  # _LOGGER intialization

    MAX_CHUNK_SIZE = 5000  # Larger sizzes will trigger a warning

    def __init__(
        self,
        api_url: str,
        timeout: int,
        token: Optional[str] = None,
    ):
        """Client setup function.

        Parameters
        ----------
        api_url : str
            Address from which the API is serving. It will use the default UVICORN address as default
        token : str
            Authentification token. A non-secured logging will be considered the default case.
        timeout : int
            Seconds to considered a connection timeout. Optional
        """

        self._client = None  # Variable to store the client after the init

        try:
            response = requests.get(url=api_url + "/openapi.json").status_code
        except ConnectionRefusedError:
            raise Exception("Connection Refused: cannot connect to the API.")

        if response != 200:  # Incorrect authentification
            # default
            raise Exception("Unidentified error, it should not get here.")

        # Non-token case
        if token is None:
            self._client = Client(base_url=api_url, timeout=timeout)

        # Token case
        else:
            self._client = AuthenticatedClient(
                base_url=api_url, token=token, timeout=timeout
            )

            response_token = requests.get(
                url=api_url + "/api/me", headers=self._client.get_headers()
            ).status_code

            if response_token == 401:
                raise Exception("Authentification error: invalid credentials.")

    def log(
        self,
        records: Iterable[Any],
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

        """Check chunk_size <= length of training dataset not needed, as the Python slice system will adjust
        a bigger-than-possible length to the whole list, having all input in the same chunk.
        However, a desired check can be placed to create a custom chunk_size when that limit is exceeded
        """

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
            record_class = models.TextClassificationRecord

        elif record_type is TokenClassificationRecord:
            bulk_class = models.TokenClassificationBulkData
            bulk_records_function = token_classification_bulk.sync_detailed
            tags = models.TokenClassificationBulkDataTags.from_dict(tags)
            metadata = models.TokenClassificationBulkDataMetadata.from_dict(metadata)
            record_class = models.TokenClassificationRecord

        # Record type is not recognised
        else:
            raise Exception("Unknown record type passed as argument.")
            # TODO: podriamos tener una lista con todos los tipos posibles, y imprimir las posibilidades de records.

        for i in range(0, len(records), chunk_size):
            chunk = records[i : i + chunk_size]

            response = bulk_records_function(
                client=self._client,
                name=name,
                json_body=bulk_class(
                    tags=tags,
                    metadata=metadata,
                    records=[record_class.from_dict(r.asdict()) for r in chunk],
                ),
            )

            _check_response_errors(response)
            processed += response.parsed.processed
            failed += response.parsed.failed

        # Creating a composite BulkResponse with the total processed and failed
        return BulkResponse(dataset=name, processed=processed, failed=failed)

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
