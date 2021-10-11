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
This module contains the interface to access Rubrix's REST API.
"""


import logging
import os
import re
from typing import Iterable

import pandas
import pkg_resources

from rubrix._constants import DEFAULT_API_KEY
from rubrix.client import RubrixClient
from rubrix.client.models import *

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    # package is not installed
    pass

_LOGGER = logging.getLogger(__name__)

_client: Optional[
    RubrixClient
] = None  # Client will be stored here to pass it through functions


def _client_instance() -> RubrixClient:
    """Checks module instance client and init if not initialized."""

    global _client
    # Calling a by-default-init if it was not called before
    if _client is None:
        init()
    return _client


def init(
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout: int = 60,
) -> None:
    """Init the python client.

    Passing an api_url disables environment variable reading, which will provide
    default values.

    Args:
        api_url:
            Address of the REST API. If `None` (default) and the env variable ``RUBRIX_API_URL`` is not set,
            it will default to `http://localhost:6900`.
        api_key:
            Authentification key for the REST API. If `None` (default) and the env variable ``RUBRIX_API_KEY``
            is not set, it will default to `rubrix.apikey`.
        timeout:
            Wait `timeout` seconds for the connection to timeout. Default: 60.

    Examples:
        >>> import rubrix as rb
        >>> rb.init(api_url="http://localhost:9090", api_key="4AkeAPIk3Y")
    """

    global _client

    final_api_url = api_url or os.getenv("RUBRIX_API_URL", "http://localhost:6900")

    # Checking that the api_url does not end in '/'
    final_api_url = re.sub(r"\/$", "", final_api_url)

    # If an api_url is passed, tokens obtained via environ vars are disabled
    final_key = api_key or os.getenv("RUBRIX_API_KEY", DEFAULT_API_KEY)

    _LOGGER.info(f"Rubrix has been initialized on {final_api_url}")

    _client = RubrixClient(
        api_url=final_api_url,
        api_key=final_key,
        timeout=timeout,
    )


def log(
    records: Union[Record, Iterable[Record]],
    name: str,
    tags: Optional[Dict[str, str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    chunk_size: int = 500,
) -> BulkResponse:
    """Log Records to Rubrix.

    Args:
        records:
            The record or an iterable of records.
        name:
            The dataset name.
        tags:
            A dictionary of tags related to the dataset.
        metadata:
            A dictionary of extra info for the dataset.
        chunk_size:
            The chunk size for a data bulk.

    Returns:
        Summary of the response from the REST API

    Examples:
        >>> import rubrix as rb
        >>> record = rb.TextClassificationRecord(
        ...     inputs={"text": "my first rubrix example"},
        ...     prediction=[('spam', 0.8), ('ham', 0.2)]
        ... )
        >>> response = rb.log(record, name="example-dataset")
    """

    # Records can be a single object or a list. In case it is a single object, we create a single-element list
    # This check filter dictionaries and string based objects (that are iterables too but we don't want to
    # wrap in a list)
    if not (
        isinstance(records, Iterable)
        and not isinstance(records, (dict, str, bytes, *Record.__args__))
    ):
        records = [records]

    # noinspection PyTypeChecker,PydanticTypeChecker
    return _client_instance().log(
        records=records, name=name, tags=tags, metadata=metadata, chunk_size=chunk_size
    )


def copy(dataset: str, name_of_copy: str):
    """Creates a copy of a dataset including its tags and metadata

    Args:
        dataset:
            Name of the source dataset
        name_of_copy:
            Name of the copied dataset

    Examples:
        >>> import rubrix as rb
        >>> rb.copy("my_dataset", name_of_copy="new_dataset")
        >>> dataframe = rb.load("new_dataset")
    """
    _client_instance().copy(source=dataset, target=name_of_copy)


def load(
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

    Examples:
        >>> import rubrix as rb
        >>> dataframe = rb.load(name="example-dataset")
    """
    return _client_instance().load(name=name, limit=limit, ids=ids)


def delete(name: str) -> None:
    """Delete a dataset.

    Args:
        name:
            The dataset name.

    Examples:
        >>> import rubrix as rb
        >>> rb.delete(name="example-dataset")
    """
    _client_instance().delete(name=name)
