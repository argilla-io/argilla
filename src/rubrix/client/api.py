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
import logging
import os
import re
from functools import wraps
from inspect import signature
from typing import Any, Callable, Dict, Iterable, List, Optional, Union

import pandas
from tqdm.auto import tqdm

from rubrix._constants import (
    DATASET_NAME_REGEX_PATTERN,
    DEFAULT_API_KEY,
    RUBRIX_WORKSPACE_HEADER_NAME,
)
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
from rubrix.client.sdk.commons.errors import RubrixClientError
from rubrix.client.sdk.commons.models import Response
from rubrix.client.sdk.datasets import api as datasets_api
from rubrix.client.sdk.datasets.models import CopyDatasetRequest, TaskType
from rubrix.client.sdk.metrics import api as metrics_api
from rubrix.client.sdk.metrics.models import MetricInfo
from rubrix.client.sdk.text2text import api as text2text_api
from rubrix.client.sdk.text2text.models import (
    CreationText2TextRecord,
    Text2TextBulkData,
    Text2TextQuery,
)
from rubrix.client.sdk.text_classification import api as text_classification_api
from rubrix.client.sdk.text_classification.models import (
    CreationTextClassificationRecord,
    LabelingRule,
    LabelingRuleMetricsSummary,
    TextClassificationBulkData,
    TextClassificationQuery,
)
from rubrix.client.sdk.token_classification import api as token_classification_api
from rubrix.client.sdk.token_classification.models import (
    CreationTokenClassificationRecord,
    TokenClassificationBulkData,
    TokenClassificationQuery,
)
from rubrix.client.sdk.users.api import whoami
from rubrix.client.sdk.users.models import User

_LOGGER = logging.getLogger(__name__)
_WARNED_ABOUT_AS_PANDAS = False

# Larger sizes will trigger a warning
_MAX_CHUNK_SIZE = 5000


class Api:
    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        workspace: Optional[str] = None,
        timeout: int = 60,
    ):
        """Init the Python client.

        We will automatically init a default client for you when calling other client methods.
        The arguments provided here will overwrite your corresponding environment variables.

        Args:
            api_url: Address of the REST API. If `None` (default) and the env variable ``RUBRIX_API_URL`` is not set,
                it will default to `http://localhost:6900`.
            api_key: Authentification key for the REST API. If `None` (default) and the env variable ``RUBRIX_API_KEY``
                is not set, it will default to `rubrix.apikey`.
            workspace: The workspace to which records will be logged/loaded. If `None` (default) and the
                env variable ``RUBRIX_WORKSPACE`` is not set, it will default to the private user workspace.
            timeout: Wait `timeout` seconds for the connection to timeout. Default: 60.

        Examples:
            >>> import rubrix as rb
            >>> rb.init(api_url="http://localhost:9090", api_key="4AkeAPIk3Y")
        """
        api_url = api_url or os.getenv("RUBRIX_API_URL", "http://localhost:6900")
        # Checking that the api_url does not end in '/'
        api_url = re.sub(r"\/$", "", api_url)
        api_key = api_key or os.getenv("RUBRIX_API_KEY", DEFAULT_API_KEY)
        workspace = workspace or os.getenv("RUBRIX_WORKSPACE")

        self._client: AuthenticatedClient = AuthenticatedClient(
            base_url=api_url, token=api_key, timeout=timeout
        )
        self._user: User = whoami(client=self._client)

        if workspace is not None:
            self.set_workspace(workspace)

    def set_workspace(self, workspace: str):
        """Sets the active workspace.

        Args:
            workspace: The new workspace
        """
        if workspace is None:
            raise Exception("Must provide a workspace")

        if workspace != self.get_workspace():
            if workspace == self._user.username:
                self._client.headers.pop(RUBRIX_WORKSPACE_HEADER_NAME, workspace)
            elif (
                self._user.workspaces is not None
                and workspace not in self._user.workspaces
            ):
                raise Exception(f"Wrong provided workspace {workspace}")
            self._client.headers[RUBRIX_WORKSPACE_HEADER_NAME] = workspace

    def get_workspace(self) -> str:
        """Returns the name of the active workspace.

        Returns:
            The name of the active workspace as a string.
        """
        return self._client.headers.get(
            RUBRIX_WORKSPACE_HEADER_NAME, self._user.username
        )

    def copy(self, dataset: str, name_of_copy: str, workspace: str = None):
        """Creates a copy of a dataset including its tags and metadata

        Args:
            dataset: Name of the source dataset
            name_of_copy: Name of the copied dataset
            workspace: If provided, dataset will be copied to that workspace

        Examples:
            >>> import rubrix as rb
            >>> rb.copy("my_dataset", name_of_copy="new_dataset")
            >>> rb.load("new_dataset")
        """
        response = datasets_api.copy_dataset(
            client=self._client,
            name=dataset,
            json_body=CopyDatasetRequest(name=name_of_copy, target_workspace=workspace),
        )

        if response.status_code == 409:
            raise RuntimeError(f"A dataset with name '{name_of_copy}' already exists.")

    def delete(self, name: str) -> None:
        """Deletes a dataset.

        Args:
            name: The dataset name.

        Examples:
            >>> import rubrix as rb
            >>> rb.delete(name="example-dataset")
        """
        response = datasets_api.delete_dataset(client=self._client, name=name)
        self.check_response_errors(response)

    def log(
        self,
        records: Union[Record, Iterable[Record], Dataset],
        name: str,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 500,
        verbose: bool = True,
    ) -> BulkResponse:
        """Logs Records to Rubrix.

        Args:
            records: The record, an iterable of records, or a dataset to log.
            name: The dataset name.
            tags: A dictionary of tags related to the dataset.
            metadata: A dictionary of extra info for the dataset.
            chunk_size: The chunk size for a data bulk.
            verbose: If True, shows a progress bar and prints out a quick summary at the end.

        Returns:
            Summary of the response from the REST API

        Examples:
            >>> import rubrix as rb
            >>> record = rb.TextClassificationRecord(
            ...     text="my first rubrix example",
            ...     prediction=[('spam', 0.8), ('ham', 0.2)]
            ... )
            >>> rb.log(record, name="example-dataset")
            1 records logged to http://localhost:6900/datasets/rubrix/example-dataset
            BulkResponse(dataset='example-dataset', processed=1, failed=0)
        """
        if not name:
            raise InputValueError("Empty dataset name has been passed as argument.")

        if not re.match(DATASET_NAME_REGEX_PATTERN, name):
            raise InputValueError(
                f"Provided dataset name {name} does not match the pattern {DATASET_NAME_REGEX_PATTERN}. "
                "Please, use a valid name for your dataset"
            )

        if isinstance(records, Record.__args__):
            records = [records]
        # this transforms a Dataset* to a list of *Record
        records = list(records)

        tags = tags or {}
        metadata = metadata or {}

        try:
            record_type = type(records[0])
        except IndexError:
            raise InputValueError("Empty record list has been passed as argument.")

        if chunk_size > _MAX_CHUNK_SIZE:
            _LOGGER.warning(
                """The introduced chunk size is noticeably large, timeout errors may occur.
                Consider a chunk size smaller than %s""",
                _MAX_CHUNK_SIZE,
            )

        if record_type is TextClassificationRecord:
            bulk_class = TextClassificationBulkData
            bulk_records_function = text_classification_api.bulk
            to_sdk_model = CreationTextClassificationRecord.from_client

        elif record_type is TokenClassificationRecord:
            bulk_class = TokenClassificationBulkData
            bulk_records_function = token_classification_api.bulk
            to_sdk_model = CreationTokenClassificationRecord.from_client

        elif record_type is Text2TextRecord:
            bulk_class = Text2TextBulkData
            bulk_records_function = text2text_api.bulk
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

            self.check_response_errors(response)
            processed += response.parsed.processed
            failed += response.parsed.failed

            progress_bar.update(len(chunk))
        progress_bar.close()

        # TODO: improve logging policy in library
        if verbose:
            workspace = self.get_workspace()
            if (
                not workspace
            ):  # Just for backward comp. with datasets with no workspaces
                workspace = "-"
            print(
                f"{processed} records logged to {self._client.base_url + '/datasets/' + workspace + '/' + name}"
            )

        # Creating a composite BulkResponse with the total processed and failed
        return BulkResponse(dataset=name, processed=processed, failed=failed)

    def load(
        self,
        name: str,
        query: Optional[str] = None,
        ids: Optional[List[Union[str, int]]] = None,
        limit: Optional[int] = None,
        as_pandas: bool = True,
    ) -> Union[pandas.DataFrame, Dataset]:
        """Loads a dataset as a pandas DataFrame or a Dataset.

        Args:
            name: The dataset name.
            query: An ElasticSearch query with the
                `query string syntax <https://rubrix.readthedocs.io/en/stable/reference/webapp/search_records.html>`_
            ids: If provided, load dataset records with given ids.
            limit: The number of records to retrieve.
            as_pandas: If True, return a pandas DataFrame. If False, return a Dataset.

        Returns:
            The dataset as a pandas Dataframe or a Dataset.

        Examples:
            >>> import rubrix as rb
            >>> dataframe = rb.load(name="example-dataset")
            >>> dataset = rb.load(name="example-dataset")
        """
        response = datasets_api.get_dataset(client=self._client, name=name)
        self.check_response_errors(response)
        task = response.parsed.task

        task_config = {
            TaskType.text_classification: (
                text_classification_api.data,
                TextClassificationQuery,
                DatasetForTextClassification,
            ),
            TaskType.token_classification: (
                token_classification_api.data,
                TokenClassificationQuery,
                DatasetForTokenClassification,
            ),
            TaskType.text2text: (
                text2text_api.data,
                Text2TextQuery,
                DatasetForText2Text,
            ),
        }

        try:
            get_dataset_data, request_class, dataset_class = task_config[task]
        except KeyError:
            raise ValueError(
                f"Load method not supported for the '{task}' task. Supported tasks: "
                f"{[TaskType.text_classification, TaskType.token_classification, TaskType.text2text]}"
            )
        response = get_dataset_data(
            client=self._client,
            name=name,
            request=request_class(ids=ids, query_text=query),
            limit=limit,
        )

        self.check_response_errors(response)

        records = [sdk_record.to_client() for sdk_record in response.parsed]
        try:
            records_sorted_by_id = sorted(records, key=lambda x: x.id)
        # record ids can be a mix of int/str -> sort all as str type
        except TypeError:
            records_sorted_by_id = sorted(records, key=lambda x: str(x.id))

        dataset = dataset_class(records_sorted_by_id)

        global _WARNED_ABOUT_AS_PANDAS
        if not _WARNED_ABOUT_AS_PANDAS:
            _LOGGER.warning(
                "The argument 'as_pandas' in `rb.load` will be deprecated in the future, and we will always return a `Dataset`. "
                "To emulate the future behavior set `as_pandas=False`. To get a pandas DataFrame, call `Dataset.to_pandas()`"
            )
            _WARNED_ABOUT_AS_PANDAS = True

        if as_pandas:
            return dataset.to_pandas()
        return dataset

    def dataset_metrics(self, name: str) -> List[MetricInfo]:
        response = datasets_api.get_dataset(self._client, name)
        self.check_response_errors(response)

        response = metrics_api.get_dataset_metrics(
            self._client, name=name, task=response.parsed.task
        )
        self.check_response_errors(response)

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
        response = datasets_api.get_dataset(self._client, name)
        self.check_response_errors(response)

        metric_ = self.get_metric(name, metric=metric)
        assert metric_ is not None, f"Metric {metric} not found !!!"

        response = metrics_api.compute_metric(
            self._client,
            name=name,
            task=response.parsed.task,
            metric=metric,
            query=query,
            interval=interval,
            size=size,
        )
        self.check_response_errors(response)
        return MetricResults(**metric_.dict(), results=response.parsed)

    def fetch_dataset_labeling_rules(self, dataset: str) -> List[LabelingRule]:
        response = text_classification_api.fetch_dataset_labeling_rules(
            self._client, name=dataset
        )
        self.check_response_errors(response)

        return [LabelingRule.parse_obj(data) for data in response.parsed]

    def rule_metrics_for_dataset(
        self, dataset: str, rule: LabelingRule
    ) -> LabelingRuleMetricsSummary:
        response = text_classification_api.dataset_rule_metrics(
            self._client, name=dataset, query=rule.query, label=rule.label
        )
        self.check_response_errors(response)

        return LabelingRuleMetricsSummary.parse_obj(response.parsed)

    @staticmethod
    def check_response_errors(response: Response) -> None:
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


ACTIVE_API: Optional[Api] = None


def active_api() -> Api:
    """Returns the active API.

    If Active API is None, initialize a default one.
    """
    global ACTIVE_API
    if ACTIVE_API is None:
        ACTIVE_API = Api()
    return ACTIVE_API


def api_wrapper(api_method: Callable):
    """Decorator to wrap the API methods in module functions.

    Propagates the docstrings and adapts the signature of the methods.
    """

    def decorator(func):
        @wraps(api_method)
        def wrapped_func(*args, **kwargs):
            return func(*args, **kwargs)

        sign = signature(api_method)
        wrapped_func.__signature__ = sign.replace(
            parameters=[val for key, val in sign.parameters.items() if key != "self"]
        )
        return wrapped_func

    return decorator


@api_wrapper(Api.__init__)
def init(*args, **kwargs):
    global ACTIVE_API
    ACTIVE_API = Api(*args, **kwargs)


@api_wrapper(Api.set_workspace)
def set_workspace(*args, **kwargs):
    return active_api().set_workspace(*args, **kwargs)


@api_wrapper(Api.get_workspace)
def get_workspace(*args, **kwargs):
    return active_api().get_workspace(*args, **kwargs)


@api_wrapper(Api.copy)
def copy(*args, **kwargs):
    return active_api().copy(*args, **kwargs)


@api_wrapper(Api.delete)
def delete(*args, **kwargs):
    return active_api().delete(*args, **kwargs)


@api_wrapper(Api.log)
def log(*args, **kwargs):
    return active_api().log(*args, **kwargs)


@api_wrapper(Api.load)
def load(*args, **kwargs):
    return active_api().load(*args, **kwargs)


class InputValueError(RubrixClientError):
    pass
