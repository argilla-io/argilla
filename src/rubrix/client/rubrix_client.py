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
"""
The Rubrix client, used by the rubrix.__init__ module.
DEPRECATED, CAN BE REMOVED IN A FUTURE VERSION. USE THE rubrix.client.api MODULE INSTEAD!
"""

import logging
import socket
import warnings
from typing import Any, Dict, Iterable, List, Optional, Union

import pandas
from tqdm.auto import tqdm

from rubrix._constants import RUBRIX_WORKSPACE_HEADER_NAME
from rubrix.client.datasets import (
    Dataset,
    DatasetForText2Text,
    DatasetForTextClassification,
    DatasetForTokenClassification,
)
from rubrix.client.metrics.models import MetricResults
from rubrix.client.models import (
    BulkResponse,
    Record,
    Text2TextRecord,
    TextClassificationRecord,
    TokenClassificationRecord,
)
from rubrix.client.sdk.client import AuthenticatedClient
from rubrix.client.sdk.commons.api import bulk
from rubrix.client.sdk.commons.errors import RubrixClientError
from rubrix.client.sdk.commons.models import Response
from rubrix.client.sdk.datasets.api import copy_dataset, delete_dataset, get_dataset
from rubrix.client.sdk.datasets.models import CopyDatasetRequest, TaskType
from rubrix.client.sdk.metrics.api import compute_metric, get_dataset_metrics
from rubrix.client.sdk.metrics.models import MetricInfo
from rubrix.client.sdk.text2text.api import data as text2text_data
from rubrix.client.sdk.text2text.models import (
    CreationText2TextRecord,
    Text2TextBulkData,
    Text2TextQuery,
)
from rubrix.client.sdk.text_classification.api import data as text_classification_data
from rubrix.client.sdk.text_classification.api import (
    dataset_rule_metrics,
    fetch_dataset_labeling_rules,
)
from rubrix.client.sdk.text_classification.models import (
    CreationTextClassificationRecord,
    LabelingRule,
    LabelingRuleMetricsSummary,
    TextClassificationBulkData,
    TextClassificationQuery,
)
from rubrix.client.sdk.token_classification.api import data as token_classification_data
from rubrix.client.sdk.token_classification.models import (
    CreationTokenClassificationRecord,
    TokenClassificationBulkData,
    TokenClassificationQuery,
)
from rubrix.client.sdk.users.api import whoami
from rubrix.client.sdk.users.models import User


class InputValueError(RubrixClientError):
    pass


class RubrixClient:
    """DEPRECATED. Class definition for Rubrix Client"""

    _LOGGER = logging.getLogger(__name__)

    # Larger sizes will trigger a warning
    MAX_CHUNK_SIZE = 5000

    MACHINE_NAME = socket.gethostname()

    def __init__(
        self,
        api_url: str,
        api_key: str,
        workspace: Optional[str] = None,
        timeout: int = 60,
    ):
        """DEPRECATED. Client setup function.

        Args:
            api_url: Address from which the API is serving.
            api_key: Authentication token.
            workspace: Active workspace for this client session.
            timeout: Seconds to wait before raising a connection timeout.
        """
        warnings.warn(
            f"The 'RubrixClient' class is deprecated and will be removed in a future version! "
            f"Use the `rubrix.client.api` module instead. Make sure to adapt your code.",
            category=FutureWarning,
        )

        self._client = AuthenticatedClient(
            base_url=api_url, token=api_key, timeout=timeout
        )

        self.__current_user__: User = whoami(client=self._client)
        if workspace:
            self.set_workspace(workspace)

    def set_workspace(self, workspace: str):
        """Changes/updates the current client session workspace"""
        if workspace is None:
            raise Exception("Must provide a workspace")

        if workspace != self.active_workspace:
            if workspace == self.__current_user__.username:
                self._client.headers.pop(RUBRIX_WORKSPACE_HEADER_NAME, None)
                return
            user_workspaces = self.__current_user__.workspaces
            if user_workspaces is not None and workspace not in user_workspaces:
                raise Exception(f"Wrong provided workspace {workspace}")
            self._client.headers[RUBRIX_WORKSPACE_HEADER_NAME] = workspace

    @property
    def active_workspace(self):
        """Return the active workspace for client session"""
        return self._client.headers.get(
            RUBRIX_WORKSPACE_HEADER_NAME, self.__current_user__.username
        )

    def log(
        self,
        records: Union[Record, Iterable[Record], Dataset],
        name: str,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 500,
        verbose: bool = True,
    ) -> BulkResponse:
        """Log records to Rubrix.

        Args:
            records: The records to be logged.
            name: The dataset name.
            tags: A set of tags related to the dataset.
            metadata: A set of extra info for the dataset.
            chunk_size: Records are logged in chunks to the Rubrix server, this defines their sizes.
            verbose: If True, shows a progress bar and prints out a quick summary at the end.

        Returns:
            A summary response from the API.
        """

        if not name:
            raise InputValueError("Empty project name has been passed as argument.")

        if isinstance(records, Record.__args__):
            records = [records]

        records = list(records)
        tags = tags or {}
        metadata = metadata or {}

        try:
            record_type = type(records[0])
        except IndexError:
            raise InputValueError("Empty record list has been passed as argument.")

        # Check chunk_size <= length of training dataset not needed, as the Python slice system will adjust
        # a bigger-than-possible length to the whole list, having all input in the same chunk.
        # However, a desired check can be placed to create a custom chunk_size when that limit is exceeded
        if chunk_size > self.MAX_CHUNK_SIZE:
            self._LOGGER.warning(
                """The introduced chunk size is noticeably large, timeout errors may occur.
                Consider a chunk size smaller than %s""",
                self.MAX_CHUNK_SIZE,
            )

        # Check record type
        if record_type is TextClassificationRecord:
            bulk_class = TextClassificationBulkData
            bulk_records_function = bulk
            to_sdk_model = CreationTextClassificationRecord.from_client

        elif record_type is TokenClassificationRecord:
            bulk_class = TokenClassificationBulkData
            bulk_records_function = bulk
            to_sdk_model = CreationTokenClassificationRecord.from_client

        elif record_type is Text2TextRecord:
            bulk_class = Text2TextBulkData
            bulk_records_function = bulk
            to_sdk_model = CreationText2TextRecord.from_client

        # Record type is not recognised
        else:
            raise InputValueError(
                f"Unknown record type passed as argument for [{','.join(map(str, records[0:5]))}...] "
                f"Available values are {Record.__args__}"
            )

        processed = 0
        failed = 0
        progress_bar = tqdm(total=len(records), disable=not verbose)
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

            progress_bar.update(len(chunk))
        progress_bar.close()

        # TODO: improve logging policy in library
        if verbose:
            print(
                f"{processed} records logged to {self._client.base_url + '/ws/' + self.active_workspace + '/' + name}"
            )

        # Creating a composite BulkResponse with the total processed and failed
        return BulkResponse(dataset=name, processed=processed, failed=failed)

    def load(
        self,
        name: str,
        query: Optional[str] = None,
        ids: Optional[List[Union[str, int]]] = None,
        limit: Optional[int] = None,
    ) -> Union[pandas.DataFrame, Dataset]:
        """Loads a dataset as a pandas DataFrame or a Dataset.

        Args:
            name: The dataset name.
            query: An ElasticSearch query with the
                `query string syntax <https://rubrix.readthedocs.io/en/stable/guides/queries.html>`_
            ids: If provided, load dataset records with given ids.
            limit: The number of records to retrieve.

        Returns:
            The dataset as a pandas Dataframe or a Dataset.
        """
        response = get_dataset(client=self._client, name=name)
        _check_response_errors(response)
        task = response.parsed.task

        task_config = {
            TaskType.text_classification: (
                text_classification_data,
                TextClassificationQuery,
                DatasetForTextClassification,
            ),
            TaskType.token_classification: (
                token_classification_data,
                TokenClassificationQuery,
                DatasetForTokenClassification,
            ),
            TaskType.text2text: (
                text2text_data,
                Text2TextQuery,
                DatasetForText2Text,
            ),
        }

        try:
            get_dataset_data, request_class, dataset_class = task_config[task]
        except KeyError:
            raise ValueError(
                f"Sorry, load method not supported for the '{task}' task. Supported tasks: "
                f"{[TaskType.text_classification, TaskType.token_classification, TaskType.text2text]}"
            )
        response = get_dataset_data(
            client=self._client,
            name=name,
            request=request_class(ids=ids, query_text=query),
            limit=limit,
        )

        _check_response_errors(response)

        records = [sdk_record.to_client() for sdk_record in response.parsed]
        try:
            records_sorted_by_id = sorted(records, key=lambda x: x.id)
        # record ids can be a mix of int/str -> sort all as str type
        except TypeError:
            records_sorted_by_id = sorted(records, key=lambda x: str(x.id))

        dataset = dataset_class(records_sorted_by_id)

        return dataset

    def copy(self, source: str, target: str, target_workspace: Optional[str] = None):
        """Makes a copy of the `source` dataset and saves it as `target`"""
        response = copy_dataset(
            client=self._client,
            name=source,
            json_body=CopyDatasetRequest(
                name=target, target_workspace=target_workspace
            ),
        )
        if response.status_code == 409:
            raise RuntimeError(f"A dataset with name '{target}' already exists.")

    def delete(self, name: str):
        """Delete a dataset with given name

        Args:
            name: The dataset name
        """
        response = delete_dataset(client=self._client, name=name)
        _check_response_errors(response)

    def dataset_metrics(self, name: str) -> List[MetricInfo]:
        response = get_dataset(self._client, name)
        _check_response_errors(response)

        response = get_dataset_metrics(
            self._client, name=name, task=response.parsed.task
        )
        _check_response_errors(response)

        return response.parsed

    def get_metric(self, name: str, metric: str) -> Optional[MetricInfo]:
        metrics = self.dataset_metrics(name)
        for metric_ in metrics:
            if metric_.id == metric:
                return metric_

    def compute_metric(
        self,
        name: str,
        metric: str,
        query: Optional[str] = None,
        interval: Optional[float] = None,
        size: Optional[int] = None,
    ) -> MetricResults:
        response = get_dataset(self._client, name)
        _check_response_errors(response)

        metric_ = self.get_metric(name, metric=metric)
        assert metric_ is not None, f"Metric {metric} not found !!!"

        response = compute_metric(
            self._client,
            name=name,
            task=response.parsed.task,
            metric=metric,
            query=query,
            interval=interval,
            size=size,
        )
        _check_response_errors(response)
        return MetricResults(**metric_.dict(), results=response.parsed)

    def fetch_dataset_labeling_rules(self, dataset: str) -> List[LabelingRule]:
        response = fetch_dataset_labeling_rules(self._client, name=dataset)
        _check_response_errors(response)

        return [LabelingRule.parse_obj(data) for data in response.parsed]

    def rule_metrics_for_dataset(
        self, dataset: str, rule: LabelingRule
    ) -> LabelingRuleMetricsSummary:
        response = dataset_rule_metrics(
            self._client, name=dataset, query=rule.query, label=rule.label
        )
        _check_response_errors(response)

        return LabelingRuleMetricsSummary.parse_obj(response.parsed)


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
