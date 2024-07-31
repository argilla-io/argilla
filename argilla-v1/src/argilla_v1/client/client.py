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
import warnings
from asyncio import Future
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import backoff
import httpx
from rich import print as rprint
from rich.progress import Progress

from argilla_v1._constants import (
    DATASET_NAME_REGEX_PATTERN,
    DEFAULT_API_KEY,
    DEFAULT_API_URL,
    DEFAULT_USERNAME,
    WORKSPACE_HEADER_NAME,
    WORKSPACE_NAME_REGEX_PATTERN,
)
from argilla_v1.client.apis.datasets import Datasets
from argilla_v1.client.apis.metrics import MetricsAPI
from argilla_v1.client.apis.search import Search, VectorSearch
from argilla_v1.client.apis.status import Status
from argilla_v1.client.datasets import (
    Dataset,
    DatasetForText2Text,
    DatasetForTextClassification,
    DatasetForTokenClassification,
)
from argilla_v1.client.metrics.models import MetricResults
from argilla_v1.client.models import (
    BulkResponse,
    Record,
    Text2TextRecord,
    TextClassificationRecord,
    TokenClassificationRecord,
)
from argilla_v1.client.sdk.client import AuthenticatedClient
from argilla_v1.client.sdk.commons.api import bulk
from argilla_v1.client.sdk.commons.errors import AlreadyExistsApiError, InputValueError, NotFoundApiError
from argilla_v1.client.sdk.datasets import api as datasets_api
from argilla_v1.client.sdk.datasets.models import CopyDatasetRequest, TaskType
from argilla_v1.client.sdk.datasets.models import Dataset as DatasetModel
from argilla_v1.client.sdk.metrics import api as metrics_api
from argilla_v1.client.sdk.metrics.models import MetricInfo
from argilla_v1.client.sdk.text2text.models import (
    CreationText2TextRecord,
    Text2TextBulkData,
)
from argilla_v1.client.sdk.text2text.models import (
    Text2TextRecord as SdkText2TextRecord,
)
from argilla_v1.client.sdk.text_classification import api as text_classification_api
from argilla_v1.client.sdk.text_classification.models import (
    CreationTextClassificationRecord,
    LabelingRule,
    LabelingRuleMetricsSummary,
    TextClassificationBulkData,
)
from argilla_v1.client.sdk.text_classification.models import (
    TextClassificationRecord as SdkTextClassificationRecord,
)
from argilla_v1.client.sdk.token_classification.models import (
    CreationTokenClassificationRecord,
    TokenClassificationBulkData,
)
from argilla_v1.client.sdk.token_classification.models import (
    TokenClassificationRecord as SdkTokenClassificationRecord,
)
from argilla_v1.client.sdk.users import api as users_api
from argilla_v1.client.sdk.v1.workspaces import api as workspaces_api_v1
from argilla_v1.client.sdk.v1.workspaces.models import WorkspaceModel

_LOGGER = logging.getLogger(__name__)


class Argilla:
    """
    The main argilla client.
    """

    # Larger sizes will trigger a warning
    _MAX_BATCH_SIZE = 5000

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        workspace: Optional[str] = None,
        timeout: int = 120,
        extra_headers: Optional[Dict[str, str]] = None,
        httpx_extra_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """
        Inits `Argilla` instance.

        If called with `api_url=None` and `api_key=None` and no values have been set for the environment variables
        `ARGILLA_API_URL` and `ARGILLA_API_KEY`, then the local credentials stored by a previous call to `argilla login`
        command will be used. If local credentials are not found, then `api_url` and `api_key` will fallback to the
        default values.

        Args:
            api_url: Address of the REST API. If `None` (default) and the env variable ``ARGILLA_API_URL`` is not set,
                it will default to `http://localhost:6900`.
            api_key: Authentication key for the REST API. If `None` (default) and the env variable ``ARGILLA_API_KEY``
                is not set, it will default to `argilla.apikey`.
            workspace: The workspace to which records will be logged/loaded. If `None` (default) and the
                env variable ``ARGILLA_WORKSPACE`` is not set, it will default to the private user workspace.
            timeout: Wait `timeout` seconds for the connection to timeout. Default: 60.
            extra_headers: Extra HTTP headers sent to the server. You can use this to customize
                the headers of argilla client requests, like additional security restrictions. Default: `None`.
            httpx_extra_kwargs: Extra kwargs passed to the `httpx.Client` constructor. For more information about the
                available arguments, see https://www.python-httpx.org/api/#client. Defaults to `None`.
        """
        from argilla_v1.client.login import ArgillaCredentials

        api_url = api_url or os.getenv("ARGILLA_API_URL")
        api_key = api_key or os.getenv("ARGILLA_API_KEY")
        workspace = workspace or os.getenv("ARGILLA_WORKSPACE")
        extra_headers = extra_headers or {}

        if api_url is None and api_key is None:
            try:
                credentials = ArgillaCredentials.load()
                api_url = credentials.api_url
                api_key = credentials.api_key
                if not workspace:
                    workspace = credentials.workspace
                extra_headers = credentials.extra_headers
            except FileNotFoundError:
                pass

        api_url = api_url or DEFAULT_API_URL
        api_key = api_key or DEFAULT_API_KEY

        # Checking that the api_url does not end in '/'
        api_url = re.sub(r"\/$", "", api_url)
        headers = extra_headers or {}

        self._client: AuthenticatedClient = AuthenticatedClient(
            base_url=api_url,
            token=api_key,
            timeout=timeout,
            headers=headers.copy(),
            httpx_extra_kwargs=httpx_extra_kwargs,
        )

        self._user = users_api.whoami(client=self.http_client)  # .parsed

        if not workspace and self._user.username == DEFAULT_USERNAME and DEFAULT_USERNAME in self._user.workspaces:
            warnings.warn(
                "Default user was detected and no workspace configuration was provided,"
                f" so the default {DEFAULT_USERNAME!r} workspace will be used. If you"
                " want to setup another workspace, use the `rg.set_workspace` function"
                " or provide a different one on `rg.init`",
                category=UserWarning,
            )
            workspace = DEFAULT_USERNAME
        if workspace:
            self.set_workspace(workspace or self._user.username)
        else:
            warnings.warn(
                "No workspace configuration was detected. To work with Argilla"
                " datasets, specify a valid workspace name on `rg.init` or set it"
                " up through the `rg.set_workspace` function.",
                category=UserWarning,
            )

        self._check_argilla_versions()

    def _check_argilla_versions(self):
        from argilla_v1 import __version__ as rg_version

        api_info = Status(self.http_client).get_info()

        client_version = rg_version.split(".")[:2]
        server_version = api_info.version.split(".")[:2]
        if client_version != server_version:
            warnings.warn(
                message=f"You're connecting to Argilla Server {api_info.version} using a different client version "
                f"({rg_version}).\n"
                "This may lead to potential compatibility issues during your experience.\n"
                "To ensure a seamless and optimized connection, we highly recommend "
                "aligning your client version with the server version.",
                category=UserWarning,
            )

    def __del__(self):
        if hasattr(self, "_client"):
            del self._client

    @property
    def client(self) -> AuthenticatedClient:
        """The underlying authenticated HTTP client"""
        warnings.warn(
            message="This prop will be removed in next release. Please use the http_client prop instead.",
            category=UserWarning,
        )
        return self._client

    @property
    def http_client(self):
        """The underlying authenticated HTTP client"""
        return self._client

    @property
    def datasets(self) -> Datasets:
        """Datasets API primitives"""
        return Datasets(client=self.http_client)

    @property
    def search(self):
        """Search API primitives"""
        return Search(client=self.http_client)

    @property
    def metrics(self):
        """Metrics API primitives"""
        return MetricsAPI(client=self.http_client)

    @property
    def user(self):
        """The current connected user"""
        return self._user

    def set_workspace(self, workspace: str):
        """Sets the active workspace.

        Args:
            workspace: The new workspace
        """
        if not workspace:
            raise Exception("Must provide a workspace")

        if not re.match(WORKSPACE_NAME_REGEX_PATTERN, workspace):
            raise InputValueError(
                f"Provided workspace name {workspace} does not match the pattern"
                f" {WORKSPACE_NAME_REGEX_PATTERN}. Please, use a valid name for your"
                " workspace. This limitation is caused by naming conventions for indexes"
                " in Elasticsearch. If applicable, you can try to lowercase the name of your workspace."
                " https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-create-index.html"
            )

        if workspace != self.get_workspace():
            if workspace in [ws.name for ws in self.list_workspaces()]:
                self.http_client.update_headers({WORKSPACE_HEADER_NAME: workspace})
            else:
                raise ValueError(f"Wrong provided workspace {workspace!r}")

    def get_workspace(self) -> Optional[str]:
        """Returns the name of the active workspace.

        Returns:
            The name of the active workspace as a string.
        """
        return self.http_client.headers.get(WORKSPACE_HEADER_NAME)

    def list_workspaces(self) -> List[WorkspaceModel]:
        """Lists all the available workspaces for the current user.

        Returns:
            A list of `WorkspaceModel` objects, containing the workspace
            attributes: name, id, created_at, and updated_at.
        """
        return workspaces_api_v1.list_workspaces_me(client=self.http_client.httpx).parsed

    def list_datasets(self, workspace: Optional[str] = None) -> List[DatasetModel]:
        """Lists all the available datasets for the current user in Argilla.

        Args:
            workspace: If provided, list datasets from that workspace only. Note that
                the workspace must exist in advance, otherwise a HTTP 400 error will be
                raised.

        Returns:
            A list of `DatasetModel` objects, containing the dataset
            attributes: tags, metadata, name, id, task, owner, workspace, created_at,
            and last_updated.
        """
        return datasets_api.list_datasets(client=self.http_client, workspace=workspace).parsed

    def copy(self, dataset: str, name_of_copy: str, workspace: Optional[str] = None) -> None:
        """Creates a copy of a dataset including its tags and metadata

        Args:
            dataset: Name of the source dataset
            name_of_copy: Name of the copied dataset
            workspace: If provided, dataset will be copied to that workspace

        """
        datasets_api.copy_dataset(
            client=self.http_client,
            name=dataset,
            json_body=CopyDatasetRequest(name=name_of_copy, target_workspace=workspace),
        )

    def get_dataset(self, name: str, workspace: Optional[str] = None) -> DatasetModel:
        """Gets a dataset by name.

        Args:
            name: The dataset name.
            workspace: If provided, dataset will be retrieved from that workspace. Otherwise, the active workspace will
                be used.

        Returns:
            A `Dataset` object containing the dataset information.
        """
        response = datasets_api.get_dataset(client=self.http_client, name=name, workspace=workspace)
        return response.parsed

    def delete(self, name: str, workspace: Optional[str] = None):
        """Deletes a dataset.

        Args:
            name: The dataset name.
        """
        if workspace is not None:
            self.set_workspace(workspace)

        _LOGGER.info(f"Dataset {name} is being delete by {self._user.id}")
        datasets_api.delete_dataset(client=self.http_client, name=name)

    def log(
        self,
        records: Union[Record, Iterable[Record], Dataset],
        name: str,
        workspace: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        batch_size: int = 100,
        verbose: bool = True,
        background: bool = False,
        num_threads: int = 0,
        max_retries: int = 3,
        chunk_size: Optional[int] = None,
    ) -> Union[BulkResponse, Future]:
        """Logs Records to argilla.

        The logging happens asynchronously in a background thread.

        Args:
            records: The record, an iterable of records, or a dataset to log.
            name: The dataset name.
            tags: A dictionary of tags related to the dataset.
            metadata: A dictionary of extra info for the dataset.
            batch_size: The batch size for a data bulk.
            verbose: If True, shows a progress bar and prints out a quick summary at the end.
            background: If True, we will NOT wait for the logging process to finish and return
                an ``asyncio.Future`` object. You probably want to set ``verbose`` to False
                in that case.
            num_threads: If > 0, will use num_thread separate number threads to batches, sending data concurrently.
                Default to `0`, which means no threading at all.
            max_retries: Number of retries when logging a batch of records if a `httpx.TransportError` occurs.
                Default `3`
            chunk_size: DEPRECATED! Use `batch_size` instead.

        Returns:
            Summary of the response from the REST API.
            If the ``background`` argument is set to True, an ``asyncio.Future``
            will be returned instead.

        """

        if background:
            executor = ThreadPoolExecutor(max_workers=1)

            return executor.submit(
                self.log,
                records=records,
                name=name,
                workspace=workspace,
                tags=tags,
                metadata=metadata,
                batch_size=batch_size,
                verbose=verbose,
                chunk_size=chunk_size,
                num_threads=num_threads,
                max_retries=max_retries,
            )

        tags = tags or {}
        metadata = metadata or {}

        if workspace is not None:
            self.set_workspace(workspace)

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

        if chunk_size is not None:
            warnings.warn(
                "The argument `chunk_size` is deprecated and will be removed in a future"
                " version. Please use `batch_size` instead.",
                FutureWarning,
            )
            batch_size = chunk_size

        if batch_size > self._MAX_BATCH_SIZE:
            warnings.warn(
                "The requested batch size is noticeably large, timeout errors may occur. "
                f"Consider a batch size smaller than {self._MAX_BATCH_SIZE}",
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
            task = TaskType.text_classification
        elif record_type is TokenClassificationRecord:
            bulk_class = TokenClassificationBulkData
            creation_class = CreationTokenClassificationRecord
            task = TaskType.token_classification
        elif record_type is Text2TextRecord:
            bulk_class = Text2TextBulkData
            creation_class = CreationText2TextRecord
            task = TaskType.text2text
        else:
            raise InputValueError(f"Unknown record type {record_type}. Available values are {Record.__args__}")

        try:
            self.datasets.create(name=name, task=task, workspace=workspace)
        except AlreadyExistsApiError:
            pass

        results = []
        with Progress() as progress_bar:
            task = progress_bar.add_task("Logging...", total=len(records), visible=verbose)

            batches = [records[i : i + batch_size] for i in range(0, len(records), batch_size)]

            @backoff.on_exception(
                backoff.expo,
                exception=httpx.TransportError,
                max_tries=max_retries,
                backoff_log_level=logging.DEBUG,
            )
            def log_batch(batch_info: Tuple[int, list]) -> Tuple[int, int]:
                batch_id, batch = batch_info

                bulk_result = bulk(
                    client=self.http_client,
                    name=name,
                    json_body=bulk_class(
                        tags=tags, metadata=metadata, records=[creation_class.from_client(r) for r in batch]
                    ),
                )

                progress_bar.update(task, advance=len(batch))
                return bulk_result.processed, bulk_result.failed

            if num_threads >= 1:
                with ThreadPoolExecutor(max_workers=num_threads) as executor:
                    results.extend(list(executor.map(log_batch, enumerate(batches))))
            else:
                results.extend(list(map(log_batch, enumerate(batches))))

        processed_batches, failed_batches = zip(*results)
        processed, failed = sum(processed_batches), sum(failed_batches)

        # TODO: improve logging policy in library
        if verbose:
            _LOGGER.info(f"Processed {processed} records in dataset {name}. Failed: {failed}")
            workspace = self.get_workspace()
            if not workspace:  # Just for backward comp. with datasets with no workspaces
                workspace = "-"
            url = f"{self.http_client.base_url}/datasets/{workspace}/{name}"
            rprint(f"{processed} records logged to [link={url}]{url}[/link]")

        # Creating a composite BulkResponse with the total processed and failed
        return BulkResponse(dataset=name, processed=processed, failed=failed)

    def delete_records(
        self,
        name: str,
        workspace: Optional[str] = None,
        query: Optional[str] = None,
        ids: Optional[List[Union[str, int]]] = None,
        discard_only: bool = False,
        discard_when_forbidden: bool = True,
    ) -> Tuple[int, int]:
        """Delete records from a argilla dataset.

        Args:
            name: The dataset name.
            query: An ElasticSearch query with the `query string syntax
                <https://docs.v1.argilla.io/en/latest/practical_guides/filter_dataset.html>`_
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

        """
        if workspace is not None:
            self.set_workspace(workspace)

        return self.datasets.delete_records(
            name=name,
            mark_as_discarded=discard_only,
            discard_when_forbidden=discard_when_forbidden,
            query_text=query,
            ids=ids,
        )

    def load(
        self,
        name: str,
        workspace: Optional[str] = None,
        query: Optional[str] = None,
        vector: Optional[Tuple[str, List[float]]] = None,
        ids: Optional[List[Union[str, int]]] = None,
        limit: Optional[int] = None,
        sort: Optional[List[Tuple[str, str]]] = None,
        id_from: Optional[str] = None,
        batch_size: int = 250,
        include_vectors: bool = True,
        include_metrics: bool = True,
        as_pandas=None,
    ) -> Dataset:
        """Loads a argilla dataset.

        Args:
            name: The dataset name.
            query: An ElasticSearch query with the `query string
                syntax <https://docs.v1.argilla.io/en/latesthttps://docs.v1.argilla.io/en/latest/practical_guides/filter_dataset.html.html>`_
            vector: Vector configuration for a semantic search
            ids: If provided, load dataset records with given ids.
            limit: The number of records to retrieve.
            sort: The fields on which to sort [(<field_name>, 'asc|decs')].
            id_from: If provided, starts gathering the records starting from that Record.
                As the Records returned with the load method are sorted by ID, ´id_from´
                can be used to load using batches.
            batch_size: If provided, load `batch_size` samples per request. A lower batch
                size may help avoid timeouts.
            include_vectors: When set to `False`, indicates that the record data will be retrieved excluding its vectors,
                if any. By default, this parameter is set to `True`, meaning that vector data will be included.
            include_metrics: When set to `False`, indicates that the record data will be retrieved excluding its metrics.
                By default, this parameter is set to `True`, meaning that metrics will be included.
            as_pandas: DEPRECATED! To get a pandas DataFrame do
                ``rg.load('my_dataset').to_pandas()``.


        Returns:
            A argilla dataset.

        """
        if workspace is not None:
            self.set_workspace(workspace)

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
                "If you want a pandas DataFrame do `rg.load('my_dataset').to_pandas()`.",
            )

        return self._load_records_internal(
            name=name,
            query=query,
            vector=vector,
            ids=ids,
            limit=limit,
            sort=sort,
            id_from=id_from,
            batch_size=batch_size,
            include_vectors=include_vectors,
            include_metrics=include_metrics,
        )

    def dataset_metrics(self, name: str) -> List[MetricInfo]:
        response = datasets_api.get_dataset(self.http_client, name)
        response = metrics_api.get_dataset_metrics(self.http_client, name=name, task=response.parsed.task)

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
        response = datasets_api.get_dataset(self.http_client, name)

        metric_ = self.get_metric(name, metric=metric)
        assert metric_ is not None, f"Metric {metric} not found !!!"

        response = metrics_api.compute_metric(
            self.http_client,
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
            try:
                text_classification_api.add_dataset_labeling_rule(
                    self.http_client,
                    name=dataset,
                    rule=rule,
                )
            except AlreadyExistsApiError:
                _LOGGER.warning(f"Rule {rule} already exists. Please, update the rule instead.")
            except Exception as ex:
                _LOGGER.warning(f"Cannot create rule {rule}: {ex}")

    def update_dataset_labeling_rules(
        self,
        dataset: str,
        rules: List[LabelingRule],
    ):
        """Updates the dataset labeling rules"""
        for rule in rules:
            try:
                text_classification_api.update_dataset_labeling_rule(
                    self.http_client,
                    name=dataset,
                    rule=rule,
                )
            except NotFoundApiError:
                _LOGGER.info(f"Rule {rule} does not exists, creating...")
                text_classification_api.add_dataset_labeling_rule(self.http_client, name=dataset, rule=rule)
            except Exception as ex:
                _LOGGER.warning(f"Cannot update rule {rule}: {ex}")

    def delete_dataset_labeling_rules(self, dataset: str, rules: List[LabelingRule]):
        for rule in rules:
            try:
                text_classification_api.delete_dataset_labeling_rule(self.http_client, name=dataset, rule=rule)
            except Exception as ex:
                _LOGGER.warning(f"Cannot delete rule {rule}: {ex}")
        """Deletes the dataset labeling rules"""
        for rule in rules:
            text_classification_api.delete_dataset_labeling_rule(self.http_client, name=dataset, rule=rule)

    def fetch_dataset_labeling_rules(self, dataset: str) -> List[LabelingRule]:
        response = text_classification_api.fetch_dataset_labeling_rules(self.http_client, name=dataset)

        return [LabelingRule.parse_obj(data) for data in response.parsed]

    def rule_metrics_for_dataset(self, dataset: str, rule: LabelingRule) -> LabelingRuleMetricsSummary:
        response = text_classification_api.dataset_rule_metrics(
            self.http_client, name=dataset, query=rule.query, label=rule.label
        )

        return LabelingRuleMetricsSummary.parse_obj(response.parsed)

    def _load_records_internal(
        self,
        name: str,
        query: Optional[str] = None,
        vector: Optional[Tuple[str, List[float]]] = None,
        ids: Optional[List[Union[str, int]]] = None,
        limit: Optional[int] = None,
        sort: Optional[List[Tuple[str, str]]] = None,
        id_from: Optional[str] = None,
        batch_size: int = 250,
        include_vectors: bool = True,
        include_metrics: bool = True,
    ) -> Dataset:
        dataset = self.datasets.find_by_name(name=name)
        task = dataset.task

        task_config = {
            TaskType.text_classification: (SdkTextClassificationRecord, DatasetForTextClassification),
            TaskType.token_classification: (SdkTokenClassificationRecord, DatasetForTokenClassification),
            TaskType.text2text: (SdkText2TextRecord, DatasetForText2Text),
        }

        try:
            sdk_record_class, dataset_class = task_config[task]
        except KeyError:
            raise ValueError(
                f"Load method not supported for the '{task}' task. Supported Tasks: "
                f"{[TaskType.text_classification, TaskType.token_classification, TaskType.text2text]}"
            )

        if vector:
            if sort is not None:
                _LOGGER.warning("Results are sorted by vector similarity, so 'sort' parameter is ignored.")

            if not (include_metrics and include_vectors):
                _LOGGER.warning(
                    "Metrics and vectors cannot be excluded when using vector search. These parameters will be ignored."
                )

            vector_search = VectorSearch(name=vector[0], value=vector[1])
            results = self.search.search_records(
                name=name,
                task=task,
                size=limit or 100,
                # query args
                query_text=query,
                vector=vector_search,
            )

            return dataset_class(results.records)

        all_supported_fields = {
            "metadata.*",
            "status",
            "event_timestamp",
            "annotation*",
            "prediction*",
            "search_keywords",
            "inputs.*",
            "multi_label",
            "explanation*",
            "text",
            "tokens",
        }

        if include_vectors:
            all_supported_fields.add("vectors.*")

        if include_metrics:
            all_supported_fields.add("metrics.*")

        records = self.datasets.scan(
            name=name,
            projection=all_supported_fields,
            limit=limit,
            sort=sort,
            id_from=id_from,
            batch_size=batch_size,
            # Query
            query_text=query,
            ids=ids,
        )
        records = [sdk_record_class.parse_obj(r).to_client() for r in records]
        return dataset_class(records)
