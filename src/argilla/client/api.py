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
import asyncio
import logging
import os
import re
import warnings
from asyncio import Future
from functools import wraps
from inspect import signature
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

from tqdm.auto import tqdm

from argilla._constants import (
    _OLD_WORKSPACE_HEADER_NAME,
    DATASET_NAME_REGEX_PATTERN,
    DEFAULT_API_KEY,
    WORKSPACE_HEADER_NAME,
)
from argilla.client.apis.datasets import Datasets
from argilla.client.apis.metrics import MetricsAPI
from argilla.client.apis.searches import Searches
from argilla.client.datasets import (
    Dataset,
    DatasetForText2Text,
    DatasetForTextClassification,
    DatasetForTokenClassification,
)
from argilla.client.metrics.models import MetricResults
from argilla.client.models import (
    BulkResponse,
    Record,
    Text2TextRecord,
    TextClassificationRecord,
    TextGenerationRecord,
    TokenClassificationRecord,
)
from argilla.client.sdk.client import AuthenticatedClient
from argilla.client.sdk.commons.api import async_bulk
from argilla.client.sdk.commons.errors import BaseClientError
from argilla.client.sdk.datasets import api as datasets_api
from argilla.client.sdk.datasets.models import CopyDatasetRequest, TaskType
from argilla.client.sdk.metrics import api as metrics_api
from argilla.client.sdk.metrics.models import MetricInfo
from argilla.client.sdk.text2text import api as text2text_api
from argilla.client.sdk.text2text.models import (
    CreationText2TextRecord,
    Text2TextBulkData,
    Text2TextQuery,
)
from argilla.client.sdk.text_classification import api as text_classification_api
from argilla.client.sdk.text_classification.models import (
    CreationTextClassificationRecord,
    LabelingRule,
    LabelingRuleMetricsSummary,
    TextClassificationBulkData,
    TextClassificationQuery,
)
from argilla.client.sdk.token_classification import api as token_classification_api
from argilla.client.sdk.token_classification.models import (
    CreationTokenClassificationRecord,
    TokenClassificationBulkData,
    TokenClassificationQuery,
)
from argilla.client.sdk.users import api as users_api
from argilla.client.sdk.users.models import User
from argilla.utils import setup_loop_in_thread

_LOGGER = logging.getLogger(__name__)


class _ArgillaLogAgent:
    def __init__(self, api: "Api"):
        self.__api__ = api
        self.__loop__, self.__thread__ = setup_loop_in_thread()

    @staticmethod
    async def __log_internal__(api: "Api", *args, **kwargs):
        try:
            return await api.log_async(*args, **kwargs)
        except Exception as ex:
            _LOGGER.error(
                f"Cannot log data {args, kwargs}\n"
                f"Error of type {type(ex)}\n: {ex}. ({ex.args})"
            )
            raise ex

    def log(self, *args, **kwargs) -> Future:
        return asyncio.run_coroutine_threadsafe(
            self.__log_internal__(self.__api__, *args, **kwargs), self.__loop__
        )


class Api:
    # Larger sizes will trigger a warning
    _MAX_CHUNK_SIZE = 5000

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        workspace: Optional[str] = None,
        timeout: int = 60,
        extra_headers: Optional[Dict[str, str]] = None,
    ):
        """Init the Python client.

        We will automatically init a default client for you when calling other client methods.
        The arguments provided here will overwrite your corresponding environment variables.

        Args:
            api_url: Address of the REST API. If `None` (default) and the env variable ``ARGILLA_API_URL`` is not set,
                it will default to `http://localhost:6900`.
            api_key: Authentification key for the REST API. If `None` (default) and the env variable ``ARGILLA_API_KEY``
                is not set, it will default to `argilla.apikey`.
            workspace: The workspace to which records will be logged/loaded. If `None` (default) and the
                env variable ``ARGILLA_WORKSPACE`` is not set, it will default to the private user workspace.
            timeout: Wait `timeout` seconds for the connection to timeout. Default: 60.
            extra_headers: Extra HTTP headers sent to the server. You can use this to customize
                the headers of argilla client requests, like additional security restrictions. Default: `None`.

        Examples:
            >>> import argilla as rg
            >>> rg.init(api_url="http://localhost:9090", api_key="4AkeAPIk3Y")
            >>> # Customizing request headers
            >>> headers = {"X-Client-id":"id","X-Secret":"secret"}
            >>> rg.init(api_url="http://localhost:9090", api_key="4AkeAPIk3Y", extra_headers=headers)

        """
        api_url = api_url or os.getenv("ARGILLA_API_URL", "http://localhost:6900")
        # Checking that the api_url does not end in '/'
        api_url = re.sub(r"\/$", "", api_url)
        api_key = api_key or os.getenv("ARGILLA_API_KEY", DEFAULT_API_KEY)
        workspace = workspace or os.getenv("ARGILLA_WORKSPACE")
        headers = extra_headers or {}

        self._client: AuthenticatedClient = AuthenticatedClient(
            base_url=api_url,
            token=api_key,
            timeout=timeout,
            headers=headers.copy(),
        )

        self._user: User = users_api.whoami(client=self._client)
        if workspace is not None:
            self.set_workspace(workspace)

        self._agent = _ArgillaLogAgent(self)

    def __del__(self):
        if hasattr(self, "_client"):
            del self._client
        if hasattr(self, "_agent"):
            del self._agent

    @property
    def client(self):
        """The underlying authenticated client"""
        return self._client

    @property
    def datasets(self) -> Datasets:
        return Datasets(client=self._client)

    @property
    def searches(self):
        return Searches(client=self._client)

    @property
    def metrics(self):
        return MetricsAPI(client=self.client)

    def set_workspace(self, workspace: str):
        """Sets the active workspace.

        Args:
            workspace: The new workspace
        """
        if workspace is None:
            raise Exception("Must provide a workspace")

        if workspace != self.get_workspace():
            if workspace == self._user.username:
                self._client.headers.pop(WORKSPACE_HEADER_NAME, workspace)
            elif (
                self._user.workspaces is not None
                and workspace not in self._user.workspaces
            ):
                raise Exception(f"Wrong provided workspace {workspace}")
            self._client.headers[WORKSPACE_HEADER_NAME] = workspace
            self._client.headers[_OLD_WORKSPACE_HEADER_NAME] = workspace

    def get_workspace(self) -> str:
        """Returns the name of the active workspace.

        Returns:
            The name of the active workspace as a string.
        """
        return self._client.headers.get(WORKSPACE_HEADER_NAME, self._user.username)

    def copy(self, dataset: str, name_of_copy: str, workspace: str = None):
        """Creates a copy of a dataset including its tags and metadata

        Args:
            dataset: Name of the source dataset
            name_of_copy: Name of the copied dataset
            workspace: If provided, dataset will be copied to that workspace

        Examples:
            >>> import argilla as rg
            >>> rg.copy("my_dataset", name_of_copy="new_dataset")
            >>> rg.load("new_dataset")
        """
        datasets_api.copy_dataset(
            client=self._client,
            name=dataset,
            json_body=CopyDatasetRequest(name=name_of_copy, target_workspace=workspace),
        )

    def delete(self, name: str) -> None:
        """Deletes a dataset.

        Args:
            name: The dataset name.

        Examples:
            >>> import argilla as rg
            >>> rg.delete(name="example-dataset")
        """
        datasets_api.delete_dataset(client=self._client, name=name)

    def log(
        self,
        records: Union[Record, Iterable[Record], Dataset],
        name: str,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 500,
        verbose: bool = True,
        background: bool = False,
    ) -> Union[BulkResponse, Future]:
        """Logs Records to argilla.

        The logging happens asynchronously in a background thread.

        Args:
            records: The record, an iterable of records, or a dataset to log.
            name: The dataset name.
            tags: A dictionary of tags related to the dataset.
            metadata: A dictionary of extra info for the dataset.
            chunk_size: The chunk size for a data bulk.
            verbose: If True, shows a progress bar and prints out a quick summary at the end.
            background: If True, we will NOT wait for the logging process to finish and return an ``asyncio.Future``
                object. You probably want to set ``verbose`` to False in that case.

        Returns:
            Summary of the response from the REST API.
            If the ``background`` argument is set to True, an ``asyncio.Future`` will be returned instead.

        Examples:
            >>> import argilla as rg
            >>> record = rg.TextClassificationRecord(
            ...     text="my first argilla example",
            ...     prediction=[('spam', 0.8), ('ham', 0.2)]
            ... )
            >>> rg.log(record, name="example-dataset")
            1 records logged to http://localhost:6900/datasets/argilla/example-dataset
            BulkResponse(dataset='example-dataset', processed=1, failed=0)
            >>>
            >>> # Logging records in the background
            >>> rg.log(record, name="example-dataset", background=True, verbose=False)
            <Future at 0x7f675a1fffa0 state=pending>
        """
        future = self._agent.log(
            records=records,
            name=name,
            tags=tags,
            metadata=metadata,
            chunk_size=chunk_size,
            verbose=verbose,
        )
        if background:
            return future

        try:
            return future.result()
        finally:
            future.cancel()

    async def log_async(
        self,
        records: Union[Record, Iterable[Record], Dataset],
        name: str,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 500,
        verbose: bool = True,
    ) -> BulkResponse:
        """Logs Records to argilla with asyncio.

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
            >>> # Log asynchronously from your notebook
            >>> import asyncio
            >>> import argilla as rg
            >>> from argilla.utils import setup_loop_in_thread
            >>> loop, _ = setup_loop_in_thread()
            >>> future_response = asyncio.run_coroutine_threadsafe(
            ...     rg.log_async(my_records, dataset_name), loop
            ... )
        """
        tags = tags or {}
        metadata = metadata or {}

        if not name:
            raise InputValueError("Empty dataset name has been passed as argument.")

        if not re.match(DATASET_NAME_REGEX_PATTERN, name):
            raise InputValueError(
                f"Provided dataset name {name} does not match the pattern"
                f" {DATASET_NAME_REGEX_PATTERN}. Please, use a valid name for your"
                " dataset. This limitation is caused by naming conventions for indexes"
                " in Elasticsearch."
                " https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-create-index.html"
            )

        if chunk_size > self._MAX_CHUNK_SIZE:
            _LOGGER.warning(
                """The introduced chunk size is noticeably large, timeout errors may occur.
                Consider a chunk size smaller than %s""",
                self._MAX_CHUNK_SIZE,
            )

        if isinstance(records, Record.__args__):
            records = [records]
        records = list(records)

        try:
            record_type = type(records[0])
        except IndexError:
            raise InputValueError("Empty record list has been passed as argument.")

        if record_type is TextClassificationRecord:
            bulk_class = TextClassificationBulkData
            creation_class = CreationTextClassificationRecord
        elif record_type is TokenClassificationRecord:
            bulk_class = TokenClassificationBulkData
            creation_class = CreationTokenClassificationRecord
        elif (record_type is Text2TextRecord) or (record_type is TextGenerationRecord):
            bulk_class = Text2TextBulkData
            creation_class = CreationText2TextRecord
        else:
            raise InputValueError(
                f"Unknown record type {record_type}. Available values are"
                f" {Record.__args__}"
            )

        processed, failed = 0, 0
        progress_bar = tqdm(total=len(records), disable=not verbose)
        for i in range(0, len(records), chunk_size):
            chunk = records[i : i + chunk_size]

            response = await async_bulk(
                client=self._client,
                name=name,
                json_body=bulk_class(
                    tags=tags,
                    metadata=metadata,
                    records=[creation_class.from_client(r) for r in chunk],
                ),
            )

            processed += response.parsed.processed
            failed += response.parsed.failed

            progress_bar.update(len(chunk))
        progress_bar.close()

        # TODO: improve logging policy in library
        if verbose:
            _LOGGER.info(
                f"Processed {processed} records in dataset {name}. Failed: {failed}"
            )
            workspace = self.get_workspace()
            if (
                not workspace
            ):  # Just for backward comp. with datasets with no workspaces
                workspace = "-"
            print(
                f"{processed} records logged to"
                f" {self._client.base_url}/datasets/{workspace}/{name}"
            )

        # Creating a composite BulkResponse with the total processed and failed
        return BulkResponse(dataset=name, processed=processed, failed=failed)

    def delete_records(
        self,
        name: str,
        query: Optional[str] = None,
        ids: Optional[List[Union[str, int]]] = None,
        discard_only: bool = False,
        discard_when_forbidden: bool = True,
    ) -> Tuple[int, int]:
        """Delete records from a argilla dataset.

        Args:
            name: The dataset name.
            query: An ElasticSearch query with the `query string syntax
                <https://rubrix.readthedocs.io/en/stable/guides/queries.html>`_
            ids: If provided, deletes dataset records with given ids.
            discard_only: If `True`, matched records won't be deleted. Instead, they will be marked as `Discarded`
            discard_when_forbidden: Only super-user or dataset creator can delete records from a dataset.
                So, running "hard" deletion for other users will raise an `ForbiddenApiError` error.
                If this parameter is `True`, the client API will automatically try to mark as ``Discarded``
                records instead. Default, `True`

        Returns:
            The total of matched records and real number of processed errors. These numbers could not
            be the same if some data conflicts are found during operations (some matched records change during
            deletion).

        Examples:
            >>> ## Delete by id
            >>> import argilla as rg
            >>> rg.delete_records(name="example-dataset", ids=[1,3,5])
            >>> ## Discard records by query
            >>> import argilla as rg
            >>> rg.delete_records(name="example-dataset", query="metadata.code=33", discard_only=True)
        """
        return self.datasets.delete_records(
            name=name,
            query=query,
            ids=ids,
            mark_as_discarded=discard_only,
            discard_when_forbidden=discard_when_forbidden,
        )

    def load(
        self,
        name: str,
        query: Optional[str] = None,
        ids: Optional[List[Union[str, int]]] = None,
        limit: Optional[int] = None,
        id_from: Optional[str] = None,
        as_pandas=None,
    ) -> Dataset:
        """Loads a argilla dataset.

        Parameters:
        -----------
            name:
                The dataset name.
            query:
                An ElasticSearch query with the
                `query string syntax <https://argilla.readthedocs.io/en/stable/guides/queries.html>`_
            ids:
                If provided, load dataset records with given ids.
            limit:
                The number of records to retrieve.

            id_from:
                If provided, starts gathering the records starting from that Record. As the Records returned with the
                load method are sorted by ID, ´id_from´ can be used to load using batches.

            as_pandas:
                DEPRECATED! To get a pandas DataFrame do ``rg.load('my_dataset').to_pandas()``.

        Returns:
        --------
            A argilla dataset.

        Examples:
            **Basic Loading**: load the samples sorted by their ID
            >>> import argilla as rg
            >>> dataset = rg.load(name="example-dataset")

            **Iterate over a large dataset:**
                When dealing with a large dataset you might want to load it in batches to optimize memory consumption
                and avoid network timeouts. To that end, a simple batch-iteration over the whole database can be done
                employing the `from_id` parameter. This parameter will act as a delimiter, retrieving the N items after
                the given id, where N is determined by the `limit` parameter. **NOTE** If
                no `limit` is given the whole dataset after that ID will be retrieved.

            >>> import argilla as rg
            >>> dataset_batch_1 = rg.load(name="example-dataset", limit=1000)
            >>> dataset_batch_2 = rg.load(name="example-dataset", limit=1000, id_from=dataset_batch_1[-1].id)

        """
        if as_pandas is False:
            warnings.warn(
                "The argument `as_pandas` is deprecated and will be removed in a future"
                " version. Please adapt your code accordingly. ",
                FutureWarning,
            )
        elif as_pandas is True:
            raise ValueError(
                "The argument `as_pandas` is deprecated and will be removed in a future"
                " version. Please adapt your code accordingly. ",
                "If you want a pandas DataFrame do"
                " `rg.load('my_dataset').to_pandas()`.",
            )

        response = datasets_api.get_dataset(client=self._client, name=name)
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
                f"Load method not supported for the '{task}' task. Supported Tasks: "
                f"{[TaskType.text_classification, TaskType.token_classification, TaskType.text2text]}"
            )
        response = get_dataset_data(
            client=self._client,
            name=name,
            request=request_class(ids=ids, query_text=query),
            limit=limit,
            id_from=id_from,
        )

        records = [sdk_record.to_client() for sdk_record in response.parsed]
        try:
            records_sorted_by_id = sorted(records, key=lambda x: x.id)
        # record ids can be a mix of int/str -> sort all as str type
        except TypeError:
            records_sorted_by_id = sorted(records, key=lambda x: str(x.id))

        return dataset_class(records_sorted_by_id)

    def dataset_metrics(self, name: str) -> List[MetricInfo]:
        response = datasets_api.get_dataset(self._client, name)
        response = metrics_api.get_dataset_metrics(
            self._client, name=name, task=response.parsed.task
        )

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

        return MetricResults(**metric_.dict(), results=response.parsed)

    def add_dataset_labeling_rules(self, dataset: str, rules: List[LabelingRule]):
        """Adds the dataset labeling rules"""
        for rule in rules:
            text_classification_api.add_dataset_labeling_rule(
                self._client,
                name=dataset,
                rule=rule,
            )

    def update_dataset_labeling_rules(self, dataset: str, rules: List[LabelingRule]):
        """Updates the dataset labeling rules"""
        for rule in rules:
            text_classification_api.update_dataset_labeling_rule(
                self._client, name=dataset, rule=rule
            )

    def delete_dataset_labeling_rules(self, dataset: str, rules: List[LabelingRule]):
        """Deletes the dataset labeling rules"""
        for rule in rules:
            text_classification_api.delete_dataset_labeling_rule(
                self._client, name=dataset, rule=rule
            )

    def fetch_dataset_labeling_rules(self, dataset: str) -> List[LabelingRule]:
        response = text_classification_api.fetch_dataset_labeling_rules(
            self._client, name=dataset
        )

        return [LabelingRule.parse_obj(data) for data in response.parsed]

    def rule_metrics_for_dataset(
        self, dataset: str, rule: LabelingRule
    ) -> LabelingRuleMetricsSummary:
        response = text_classification_api.dataset_rule_metrics(
            self._client, name=dataset, query=rule.query, label=rule.label
        )

        return LabelingRuleMetricsSummary.parse_obj(response.parsed)


__ACTIVE_API__: Optional[Api] = None


def active_api() -> Api:
    """Returns the active API.

    If Active API is None, initialize a default one.
    """
    global __ACTIVE_API__
    if __ACTIVE_API__ is None:
        __ACTIVE_API__ = Api()
    return __ACTIVE_API__


def api_wrapper(api_method: Callable):
    """Decorator to wrap the API methods in module functions.

    Propagates the docstrings and adapts the signature of the methods.
    """

    def decorator(func):
        if asyncio.iscoroutinefunction(api_method):

            @wraps(api_method)
            async def wrapped_func(*args, **kwargs):
                return await func(*args, **kwargs)

        else:

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
    global __ACTIVE_API__
    __ACTIVE_API__ = Api(*args, **kwargs)


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


@api_wrapper(Api.log_async)
def log_async(*args, **kwargs):
    return active_api().log_async(*args, **kwargs)


@api_wrapper(Api.load)
def load(*args, **kwargs):
    return active_api().load(*args, **kwargs)


@api_wrapper(Api.delete_records)
def delete_records(*args, **kwargs):
    return active_api().delete_records(*args, **kwargs)


class InputValueError(BaseClientError):
    pass
