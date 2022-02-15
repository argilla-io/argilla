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
from typing import Any, Dict, Iterable, List, Optional, Union

import httpx
import pandas
from tqdm.auto import tqdm

from rubrix._constants import DEFAULT_API_KEY, RUBRIX_WORKSPACE_HEADER_NAME
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

# Client and User will be stored here to pass it through functions
_CLIENT: Optional[AuthenticatedClient] = None
_USER: Optional[User] = None


def init(
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
    workspace: Optional[str] = None,
    timeout: int = 60,
) -> None:
    """Init the Python client.

    Passing an api_url disables environment variable reading, which will provide
    default values.

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
    global _CLIENT

    api_url = api_url or os.getenv("RUBRIX_API_URL", "http://localhost:6900")
    # Checking that the api_url does not end in '/'
    api_url = re.sub(r"\/$", "", api_url)
    api_key = api_key or os.getenv("RUBRIX_API_KEY", DEFAULT_API_KEY)
    workspace = workspace or os.getenv("RUBRIX_WORKSPACE")

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

    _CLIENT = AuthenticatedClient(base_url=api_url, token=api_key, timeout=timeout)

    response = whoami(client=_CLIENT)
    whoami_response_status = response.status_code
    if whoami_response_status == 401:
        raise Exception("Authentication error: invalid credentials.")

    _CURRENT_USER: User = response.parsed

    if workspace:
        set_workspace(workspace)


def set_workspace(workspace: str):
    """Sets the active workspace for the current client session.

    Args:
        workspace: The new workspace
    """
    if workspace != get_workspace():
        if workspace == _USER.username:
            _CLIENT.headers.pop(RUBRIX_WORKSPACE_HEADER_NAME, None)
            return
        if _USER.workspaces is not None and workspace not in _USER.workspaces:
            raise Exception(f"Wrong provided workspace {workspace}")
        _CLIENT.headers[RUBRIX_WORKSPACE_HEADER_NAME] = workspace


def get_workspace() -> str:
    """Returns the name of the active workspace for the current client session.

    Returns:
        The name of the active workspace as a string.
    """
    if _CLIENT is None:
        init()
    return _CLIENT.headers.get(RUBRIX_WORKSPACE_HEADER_NAME, _USER.username)


def copy(dataset: str, name_of_copy: str, workspace: str = None):
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
    if _CLIENT is None:
        init()

    response = datasets_api.copy_dataset(
        client=_CLIENT,
        name=dataset,
        json_body=CopyDatasetRequest(name=name_of_copy, target_workspace=workspace),
    )

    if response.status_code == 409:
        raise RuntimeError(f"A dataset with name '{name_of_copy}' already exists.")


def delete(name: str) -> None:
    """Delete a dataset.

    Args:
        name: The dataset name.

    Examples:
        >>> import rubrix as rb
        >>> rb.delete(name="example-dataset")
    """
    if _CLIENT is None:
        init()

    response = datasets_api.delete_dataset(client=_CLIENT, name=name)
    _check_response_errors(response)


def log(
    records: Union[Record, Iterable[Record], Dataset],
    name: str,
    tags: Optional[Dict[str, str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    chunk_size: int = 500,
    verbose: bool = True,
) -> BulkResponse:
    """Log Records to Rubrix.

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
        ...     inputs={"text": "my first rubrix example"},
        ...     prediction=[('spam', 0.8), ('ham', 0.2)]
        ... )
        >>> rb.log(record, name="example-dataset")
        1 records logged to http://localhost:6900/ws/rubrix/example-dataset
        BulkResponse(dataset='example-dataset', processed=1, failed=0)
    """
    if _CLIENT is None:
        init()

    if not name:
        raise InputValueError("Empty project name has been passed as argument.")

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
            client=_CLIENT,
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
            f"{processed} records logged to {_CLIENT.base_url + '/ws/' + get_workspace() + '/' + name}"
        )

    # Creating a composite BulkResponse with the total processed and failed
    return BulkResponse(dataset=name, processed=processed, failed=failed)


def load(
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
    if _CLIENT is None:
        init()

    response = datasets_api.get_dataset(client=_CLIENT, name=name)
    _check_response_errors(response)
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
        client=_CLIENT,
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


def dataset_metrics(name: str) -> List[MetricInfo]:
    if _CLIENT is None:
        init()

    response = datasets_api.get_dataset(_CLIENT, name)
    _check_response_errors(response)

    response = metrics_api.get_dataset_metrics(
        _CLIENT, name=name, task=response.parsed.task
    )
    _check_response_errors(response)

    return response.parsed


def get_metric(name: str, metric: str) -> Optional[MetricInfo]:
    metrics = dataset_metrics(name)
    for metric_ in metrics:
        if metric_.id == metric:
            return metric_


def compute_metric(
    name: str,
    metric: str,
    query: Optional[str] = None,
    interval: Optional[float] = None,
    size: Optional[int] = None,
) -> MetricResults:
    if _CLIENT is None:
        init()

    response = datasets_api.get_dataset(_CLIENT, name)
    _check_response_errors(response)

    metric_ = get_metric(name, metric=metric)
    assert metric_ is not None, f"Metric {metric} not found !!!"

    response = metrics_api.compute_metric(
        _CLIENT,
        name=name,
        task=response.parsed.task,
        metric=metric,
        query=query,
        interval=interval,
        size=size,
    )
    _check_response_errors(response)
    return MetricResults(**metric_.dict(), results=response.parsed)


def fetch_dataset_labeling_rules(dataset: str) -> List[LabelingRule]:
    if _CLIENT is None:
        init()

    response = text_classification_api.fetch_dataset_labeling_rules(
        _CLIENT, name=dataset
    )
    _check_response_errors(response)

    return [LabelingRule.parse_obj(data) for data in response.parsed]


def rule_metrics_for_dataset(
    dataset: str, rule: LabelingRule
) -> LabelingRuleMetricsSummary:
    if _CLIENT is None:
        init()

    response = text_classification_api.dataset_rule_metrics(
        _CLIENT, name=dataset, query=rule.query, label=rule.label
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


class InputValueError(RubrixClientError):
    pass
