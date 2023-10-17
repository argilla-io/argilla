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
import warnings
from asyncio import Future
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from argilla.client.client import Argilla
from argilla.client.datasets import Dataset
from argilla.client.models import BulkResponse, Record  # TODO Remove TextGenerationRecord
from argilla.client.sdk.commons import errors
from argilla.client.sdk.datasets.models import Dataset as DatasetModel
from argilla.client.sdk.v1.datasets.api import list_datasets as list_datasets_api_v1
from argilla.client.sdk.v1.workspaces.models import WorkspaceModel
from argilla.client.sdk.workspaces.api import list_workspaces as list_workspaces_api_v0

Api = Argilla  # Backward compatibility


class ArgillaSingleton:
    """The active argilla singleton instance"""

    _INSTANCE: Optional[Argilla] = None

    @classmethod
    def get(cls) -> Argilla:
        if cls._INSTANCE is None:
            return cls.init()
        return cls._INSTANCE

    @classmethod
    def clear(cls) -> None:
        cls._INSTANCE = None

    @classmethod
    def init(
        cls,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        workspace: Optional[str] = None,
        timeout: int = 60,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Argilla:
        cls._INSTANCE = None

        cls._INSTANCE = Argilla(
            api_url=api_url,
            api_key=api_key,
            timeout=timeout,
            workspace=workspace,
            extra_headers=extra_headers,
        )

        return cls._INSTANCE


def init(
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
    workspace: Optional[str] = None,
    timeout: int = 60,
    extra_headers: Optional[Dict[str, str]] = None,
) -> None:
    """Init the Python client.

    If this function is called with `api_url=None` and `api_key=None` and no values have been set for the environment
    variables `ARGILLA_API_URL` and `ARGILLA_API_KEY`, then the local credentials stored by a previous call to `argilla
    login` command will be used. If local credentials are not found, then `api_url` and `api_key` will fallback to the
    default values.

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
        >>>
        >>> rg.init(api_url="http://localhost:9090", api_key="4AkeAPIk3Y")
        >>> # Customizing request headers
        >>> headers = {"X-Client-id":"id","X-Secret":"secret"}
        >>> rg.init(api_url="http://localhost:9090", api_key="4AkeAPIk3Y", extra_headers=headers)
    """
    ArgillaSingleton.init(
        api_url=api_url,
        api_key=api_key,
        workspace=workspace,
        timeout=timeout,
        extra_headers=extra_headers,
    )


def log(
    records: Union[Record, Iterable[Record], Dataset],
    name: str,
    workspace: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    batch_size: int = 100,
    verbose: bool = True,
    background: bool = False,
    chunk_size: Optional[int] = None,
    num_threads: int = 0,
    max_retries: int = 3,
) -> Union[BulkResponse, Future]:
    """Logs Records to argilla.

    The logging happens asynchronously in a background thread.

    Args:
        records: The record, an iterable of records, or a dataset to log.
        name: The dataset name.
        workspace: The workspace to which records will be logged/loaded. If `None` (default) and the
            env variable ``ARGILLA_WORKSPACE`` is not set, it will default to the private user workspace.
        tags: A dictionary of tags related to the dataset.
        metadata: A dictionary of extra info for the dataset.
        batch_size: The batch size for a data bulk.
        verbose: If True, shows a progress bar and prints out a quick summary at the end.
        background: If True, we will NOT wait for the logging process to finish and return an ``asyncio.Future``
            object. You probably want to set ``verbose`` to False in that case.
        chunk_size: DEPRECATED! Use `batch_size` instead.
        num_threads: If > 0, will use num_thread separate number threads to batches, sending data concurrently.
                Default to `0`, which means no threading at all.
        max_retries: Number of retries when logging a batch of records if a `httpx.TransportError` occurs.
                Default `3`.

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
    return ArgillaSingleton.get().log(
        records=records,
        name=name,
        workspace=workspace,
        tags=tags,
        metadata=metadata,
        batch_size=batch_size,
        verbose=verbose,
        background=background,
        chunk_size=chunk_size,
        num_threads=num_threads,
        max_retries=max_retries,
    )


async def log_async(
    records: Union[Record, Iterable[Record], Dataset],
    name: str,
    workspace: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    batch_size: int = 100,
    verbose: bool = True,
    chunk_size: Optional[int] = None,
) -> BulkResponse:
    """Logs Records to argilla with asyncio.

    Args:
        records: The record, an iterable of records, or a dataset to log.
        name: The dataset name.
        workspace: The workspace to which records will be logged/loaded. If `None` (default) and the
            env variable ``ARGILLA_WORKSPACE`` is not set, it will default to the private user workspace.
        tags: A dictionary of tags related to the dataset.
        metadata: A dictionary of extra info for the dataset.
        batch_size: The batch size for a data bulk.
        verbose: If True, shows a progress bar and prints out a quick summary at the end.
        chunk_size: DEPRECATED! Use `batch_size` instead.

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

    warnings.warn(
        (
            "`log_async` is deprecated and will be removed in next release. "
            "Please, use `log` with `background=True` instead"
        ),
        DeprecationWarning,
    )

    future = ArgillaSingleton.get().log(
        records=records,
        name=name,
        workspace=workspace,
        tags=tags,
        metadata=metadata,
        batch_size=batch_size,
        verbose=verbose,
        chunk_size=chunk_size,
        background=True,
    )

    return await asyncio.wrap_future(future)


def _check_if_feedback_dataset_exists(client: Argilla, name: str, workspace: str) -> bool:
    response = list_workspaces_api_v0(client.http_client.httpx)
    workspace_id = None
    for ws in response.parsed:
        if ws.name == workspace:
            workspace_id = ws.id
            break

    response = list_datasets_api_v1(client.http_client.httpx)
    for dataset in response.parsed:
        if dataset.name == name and dataset.workspace_id == workspace_id:
            return True

    return False


def load(
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
    as_pandas: Optional[bool] = None,
) -> Dataset:
    """Loads a argilla dataset.

    Args:
        name: The dataset name.
        workspace: The workspace to which records will be logged/loaded. If `None` (default) and the
            env variable ``ARGILLA_WORKSPACE`` is not set, it will default to the private user workspace.
        query: An ElasticSearch query with the `query string
            syntax <https://docs.argilla.io/en/latest/practical_guides/filter_dataset.html>`_
        vector: Vector configuration for a semantic search
        ids: If provided, load dataset records with given ids.
        limit: The number of records to retrieve.
        sort: The fields on which to sort [(<field_name>, 'asc|decs')].
        id_from: If provided, starts gathering the records starting from that Record.
            As the Records returned with the load method are sorted by ID, `id_from`
            can be used to load using batches.
        batch_size: If provided, load `batch_size` samples per request. A lower batch
            size may help avoid timeouts.
        include_vectors: When set to `False`, indicates that records will be retrieved excluding their vectors,
            if any. By default, this parameter is set to `True`, meaning that vectors will be included.
        include_metrics: When set to `False`, indicates that records will be retrieved excluding their metrics.
            By default, this parameter is set to `True`, meaning that metrics will be included.
        as_pandas: DEPRECATED! To get a pandas DataFrame do
            ``rg.load('my_dataset').to_pandas()``.

    Returns:
        A argilla dataset.

    Examples:
        **Basic Loading: load the samples sorted by their ID**

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
    argilla = ArgillaSingleton.get()
    try:
        return argilla.load(
            name=name,
            workspace=workspace,
            query=query,
            vector=vector,
            ids=ids,
            limit=limit,
            sort=sort,
            id_from=id_from,
            batch_size=batch_size,
            include_metrics=include_metrics,
            include_vectors=include_vectors,
            as_pandas=as_pandas,
        )
    except errors.NotFoundApiError as e:
        workspace = workspace or argilla.get_workspace()
        if _check_if_feedback_dataset_exists(client=argilla, name=name, workspace=workspace):
            raise ValueError(
                f"The dataset '{name}' exists but it is a `FeedbackDataset`. Use `rg.FeedbackDataset.from_argilla`"
                " instead to load it."
            )
        raise e


def copy(dataset: str, name_of_copy: str, workspace: Optional[str] = None) -> None:
    """
    Creates a copy of a dataset including its tags and metadata

    Args:
        dataset: Name of the source dataset
        name_of_copy: Name of the copied dataset
        workspace: If provided, dataset will be copied to that workspace

    Examples:
        >>> import argilla as rg
        >>> rg.copy("my_dataset", name_of_copy="new_dataset")
        >>> rg.load("new_dataset")
    """
    ArgillaSingleton.get().copy(
        dataset=dataset,
        name_of_copy=name_of_copy,
        workspace=workspace,
    )


def delete(name: str, workspace: Optional[str] = None) -> None:
    """
    Deletes a dataset.

    Args:
        name: The dataset name.
        workspace: The workspace to which records will be logged/loaded. If `None` (default) and the
            env variable ``ARGILLA_WORKSPACE`` is not set, it will default to the private user workspace.

    Examples:
        >>> import argilla as rg
        >>> rg.delete(name="example-dataset")
    """
    ArgillaSingleton.get().delete(name=name, workspace=workspace)


def delete_records(
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
        workspace: The workspace to which records will be logged/loaded. If `None` (default) and the
            env variable ``ARGILLA_WORKSPACE`` is not set, it will default to the private user workspace.
        query: An ElasticSearch query with the `query string syntax
            <https://docs.argilla.io/en/latest/practical_guides/filter_dataset.html>`_
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
    return ArgillaSingleton.get().delete_records(
        name=name,
        workspace=workspace,
        query=query,
        ids=ids,
        discard_only=discard_only,
        discard_when_forbidden=discard_when_forbidden,
    )


def set_workspace(workspace: str) -> None:
    """Sets the active workspace.

    Args:
        workspace: The new workspace
    """
    ArgillaSingleton.get().set_workspace(workspace=workspace)


def get_workspace() -> str:
    """Returns the name of the active workspace.

    Returns:
        The name of the active workspace as a string.
    """
    return ArgillaSingleton.get().get_workspace()


def list_workspaces() -> List[WorkspaceModel]:
    """Lists all the available workspaces for the current user.

    Returns:
        A list of `WorkspaceModel` objects, containing the workspace
        attributes: name, id, created_at, and updated_at.
    """
    warnings.warn(
        "`Workspace.list` is recommended over `list_workspaces`, since you can easily"
        " access the workspaces as a list of `Workspace` objects with their attributes"
        " and methods.",
        UserWarning,
        stacklevel=1,
    )
    return ArgillaSingleton.get().list_workspaces()


def list_datasets(workspace: Optional[str] = None) -> List[DatasetModel]:
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
    return ArgillaSingleton.get().list_datasets(workspace=workspace)


def active_client() -> Argilla:
    """Returns the active argilla client.

    If Active client is None, initialize a default one.
    """
    return ArgillaSingleton.get()


active_api = active_client  # backward compatibility
