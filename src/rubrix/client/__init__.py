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
import socket
from typing import Any, Dict, Iterable, List, Optional, Union

import httpx
import pandas

from rubrix.client.models import (
    BulkResponse,
    Record,
    Text2TextRecord,
    TextClassificationRecord,
    TokenAttributions,
    TokenClassificationRecord,
)
from rubrix.client.sdk.datasets.api import get_dataset
from rubrix.client.sdk.datasets.models import TaskType
from rubrix.client.sdk.text2text.api import bulk as text2text_bulk
from rubrix.client.sdk.text2text.api import data as text2text_data
from rubrix.client.sdk.text2text.models import (
    CreationText2TextRecord,
    Text2TextBulkData,
    Text2TextQuery,
)
from rubrix.client.sdk.text_classification.api import bulk as text_classification_bulk
from rubrix.client.sdk.text_classification.api import data as text_classification_data
from rubrix.client.sdk.text_classification.models import (
    CreationTextClassificationRecord,
    TextClassificationBulkData,
    TextClassificationQuery,
)
from rubrix.client.sdk.token_classification.api import bulk as token_classification_bulk
from rubrix.client.sdk.token_classification.api import data as token_classification_data
from rubrix.client.sdk.token_classification.models import (
    CreationTokenClassificationRecord,
    TokenClassificationBulkData,
    TokenClassificationQuery,
)
from rubrix.sdk import AuthenticatedClient
from rubrix.sdk.api.datasets import copy_dataset, delete_dataset
from rubrix.sdk.api.users import whoami
from rubrix.sdk.models.copy_dataset_request import CopyDatasetRequest
from rubrix.sdk.types import Response


class RubrixClient:
    """Class definition for Rubrix Client"""

    _LOGGER = logging.getLogger(__name__)

    # Larger sizes will trigger a warning
    MAX_CHUNK_SIZE = 5000

    MACHINE_NAME = socket.gethostname()

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
            bulk_class = TextClassificationBulkData
            bulk_records_function = text_classification_bulk
            to_sdk_model = CreationTextClassificationRecord.from_client

        elif record_type is TokenClassificationRecord:
            bulk_class = TokenClassificationBulkData
            bulk_records_function = token_classification_bulk
            to_sdk_model = CreationTokenClassificationRecord.from_client

        elif record_type is Text2TextRecord:
            bulk_class = Text2TextBulkData
            bulk_records_function = text2text_bulk
            to_sdk_model = CreationText2TextRecord.from_client

        # Record type is not recognised
        else:
            raise Exception(
                f"Unknown record type passed as argument for [{','.join(map(str, records[0:5]))}...] "
                f"Available values are {Record.__args__}"
            )

        processed = 0
        failed = 0
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
        response = get_dataset(client=self._client, name=name)
        _check_response_errors(response)
        task = response.parsed.task

        task_config = {
            TaskType.text_classification: (
                text_classification_data,
                None,
                TextClassificationQuery,
            ),
            TaskType.token_classification: (
                token_classification_data,
                None,
                TokenClassificationQuery,
            ),
            TaskType.text2text: (
                text2text_data,
                None,
                Text2TextQuery,
            ),
        }

        try:
            get_dataset_data, map_fn, request_class = task_config[task]
        except KeyError:
            raise ValueError(
                f"Sorry, load method not supported for the '{task}' task. Supported tasks: "
                f"{[TaskType.text_classification, TaskType.token_classification, TaskType.text2text]}"
            )
        response = get_dataset_data(
            client=self._client,
            name=name,
            request=request_class(ids=ids or []),
            limit=limit,
        )

        _check_response_errors(response)
        return pandas.DataFrame(map(lambda r: r.to_client().dict(), response.parsed))

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
