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
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Tuple, Union

from argilla.client.client import Argilla
from argilla.client.datasets import Dataset
from argilla.client.enums import DatasetType
from argilla.client.feedback.dataset.local.dataset import FeedbackDataset
from argilla.client.models import BulkResponse, Record  # TODO Remove TextGenerationRecord
from argilla.client.sdk.commons import errors
from argilla.client.sdk.datasets.models import Dataset as DatasetModel
from argilla.client.sdk.v1.workspaces.models import WorkspaceModel
from argilla.client.singleton import ArgillaSingleton

if TYPE_CHECKING:
    from argilla.client.feedback.dataset.remote.dataset import RemoteFeedbackDataset

Api = Argilla  # Backward compatibility


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
) -> Union[Dataset, "RemoteFeedbackDataset"]:
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
    except errors.ArApiResponseError as e:
        workspace = workspace or argilla.get_workspace()
        try:
            dataset = FeedbackDataset.from_argilla(name=name, workspace=workspace)
        except ValueError:
            raise e

        warnings.warn(
            "Loaded dataset is a `FeedbackDataset`. It's recommended to use "
            f"`rg.FeedbackDataset.from_argilla(name='{name}', workspace='{workspace}')` instead",
            UserWarning,
            stacklevel=2,
        )

        return dataset


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
    Deletes an Argilla dataset from the server. It can be used with both `Dataset` and `FeedbackDataset`, although
    for the latter it's recommended to use `rg.FeedbackDataset.delete` instead.

    Args:
        name: The name of the dataset to delete.
        workspace: The workspace to which the dataset belongs. If `None` (default) and the env variable
            ``ARGILLA_WORKSPACE`` is not set, it will default to the private user workspace.

    Raises:
        ValueError: If no dataset is found with the given name and workspace.
        PermissionError: If the dataset that's being deleted is a `FeedbackDataset` and the user doesn't have enough
            permissions to delete it.
        RuntimeError: If the dataset that's being deleted is a `FeedbackDataset` and some kind of error occurs during
            the deletion process.

    Examples:
        >>> import argilla as rg
        >>> rg.delete(name="example-dataset")
    """
    argilla = ArgillaSingleton.get()
    workspace = workspace or argilla.get_workspace()
    try:
        # `delete` method is always successful, even if the dataset does not exist and that's why we need the extra
        # call to `get_dataset` to check if the dataset exists. If it doesn't exist, then we try to delete a `FeedbackDataset`.
        argilla.get_dataset(name=name, workspace=workspace)
        argilla.delete(name=name, workspace=workspace)
    except errors.ArApiResponseError as e:
        try:
            dataset = FeedbackDataset.from_argilla(name=name, workspace=workspace)
        except ValueError:
            raise e

        dataset.delete()

        warnings.warn(
            "Removed dataset was a `FeedbackDataset`. It's recommended to use "
            f"`rg.FeedbackDataset.from_argilla(name='{name}', workspace='{workspace}').delete()` instead.",
            UserWarning,
            stacklevel=2,
        )


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


def list_datasets(
    workspace: Optional[str] = None, type: Optional[Union[str, DatasetType]] = None
) -> List[Union[DatasetModel, "RemoteFeedbackDataset"]]:
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
    if type is not None:
        type = type if isinstance(type, DatasetType) else DatasetType(type)

    old_datasets = []
    if type is None or type == DatasetType.other:
        old_datasets = ArgillaSingleton.get().list_datasets(workspace=workspace)

    datasets = []
    if type is None or type == DatasetType.feedback:
        datasets = FeedbackDataset.list(workspace=workspace)

    return old_datasets + datasets
