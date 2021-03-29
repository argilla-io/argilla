# -*- coding: utf-8 -*-

"""Rubrix Client Init Method

Methods for using the Rubrix Client, called from the module init file.
"""


from typing import Any, Dict, Optional, List, Union, Iterable
import logging
import requests

from rubrix.sdk import Client, AuthenticatedClient
from rubrix.sdk.models import *
from rubrix.sdk.api.text_classification import bulk_records as text_classification_bulk
from rubrix.sdk.api.token_classification import (
    bulk_records as token_classification_bulk,
)


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
            BulkClass = TextClassificationBulkData
            bulk_records_function = text_classification_bulk.sync_detailed
            tags = TextClassificationBulkDataTags.from_dict(tags)
            metadata = TextClassificationBulkDataMetadata.from_dict(metadata)

        elif record_type is TokenClassificationRecord:
            BulkClass = TokenClassificationBulkData
            bulk_records_function = token_classification_bulk.sync_detailed
            tags = TokenClassificationBulkDataTags.from_dict(tags)
            metadata = TokenClassificationBulkDataMetadata.from_dict(metadata)

        # Record type is not recognised
        else:
            raise Exception("Unknown record type passed as argument.")
            # TODO: podriamos tener una lista con todos los tipos posibles, y imprimir las posibilidades de records.

        for i in range(0, len(records), chunk_size):
            chunk = records[i : i + chunk_size]

            response = bulk_records_function(
                client=self._client,
                name=name,
                json_body=BulkClass(tags=tags, metadata=metadata, records=chunk),
            )
            # Concrete error codes
            if response.status_code == 401:
                raise Exception(
                    "Unauthorized error: invalid credentials. The API answered with a {} code: {}".format(
                        response.status_code, response.content
                    )
                )

            elif response.status_code == 403:
                raise Exception(
                    "Forbidden error: you have not been authorised to access this dataset. The API answered with a {} code: {}".format(
                        response.status_code, response.content
                    )
                )

            elif response.status_code == 404:
                raise Exception(
                    "Not found error. The API answered with a {} code: {}".format(
                        response.status_code, response.content
                    )
                )

            elif response.status_code == 422:
                raise Exception(
                    "Unprocessable entity error: Something is wrong in your records. The API answered with a {} code: {}".format(
                        response.status_code, response.content
                    )
                )

            elif (
                response.status_code >= 400
                and response.status_code < 500
                or not response.parsed
            ):
                raise Exception(
                    "Request error: API cannot answer. The API answered with a {} code: {}".format(
                        response.status_code, response.content
                    )
                )

            elif response.status_code >= 500:
                raise Exception(
                    "Connection error: API is not responding. The API answered with a {} code: {}".format(
                        response.status_code, response.content
                    )
                )

            else:
                processed += response.parsed.processed
                failed += response.parsed.failed

        # Creating a composite BulkResponse with the total processed and failed
        return BulkResponse.from_dict(
            {"dataset": name, "processed": processed, "failed": failed}
        )
