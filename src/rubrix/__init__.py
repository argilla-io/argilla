# -*- coding: utf-8 -*-

"""Rubrix Init Method

Contains methods for accesing the API.
"""

import logging
import os
import re
from typing import Iterable

import pandas
import pkg_resources
from rubrix.client import RubrixClient, models
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


def init(
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout: int = 60,
):
    """Client setup function.

    Calling the RubrixClient init function.
    Passing an api_url disables environment variable reading, which will provide
    default values.

    Parameters
    ----------
    api_url : str
        Address from which the API is serving. It will use the default UVICORN address as default
    api_key: str
        Authentification api key. A non-secured log will be considered the default case. Optional
    timeout : int
        Seconds to considered a connection timeout. Optional
    """

    global _client

    final_api_url = api_url or os.getenv("RUBRIX_API_URL", "http://localhost:6900")

    # Checking that the api_url does not ends in '/'
    final_api_url = re.sub(r"\/$", "", final_api_url)

    # If an api_url is passed, tokens obtained via environ vars are disabled
    if api_url is not None:
        final_key = api_key
    else:
        final_key = api_key or os.getenv("RUBRIX_API_KEY")

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
):
    """
    Register a set of logs into Rubrix

    Parameters
    ----------
    records:
        The data record object or list.
    name:
        The dataset name
    tags:
        A set of tags related to dataset. Optional
    metadata:
        A set of extra info for dataset. Optional
    chunk_size:
        The default chunk size for data bulk

    """

    # Records can be a single object or a list. In case it is a single object, we create a single-element list
    # This check filter dictionaries and string based objects (that are iterables too but we don't want to
    # wrap in a list)
    if not (
        isinstance(records, Iterable)
        and not isinstance(records, (dict, str, bytes, *Record.__args__))
    ):
        records = [records]

    return _client_instance().log(
        records=records, name=name, tags=tags, metadata=metadata, chunk_size=chunk_size
    )


def _client_instance() -> RubrixClient:
    """Checks module instance client and init if not initialized"""

    global _client
    # Calling a by-default-init if it was not called before
    if _client is None:
        init()
    return _client


def snapshots(dataset: str) -> List[models.DatasetSnapshot]:
    """
    Retrieve dataset snapshots

    Parameters
    ----------
    dataset:
        The dataset name

    Returns
    -------

    """
    return _client_instance().snapshots(dataset)


def load(
    name: str,
    snapshot: Optional[str] = None,
    ids: Optional[List[Union[str, int]]] = None,
    limit: Optional[int] = None,
) -> pandas.DataFrame:
    """
    Load datase/snapshot data as a huggingface dataset

    Parameters
    ----------
    name:
        The dataset name
    snapshot:
        The dataset snapshot id. Optional
    ids:
        If provided, load dataset records with given ids.
        Won't apply for snapshots
    limit:
        The number of records to retrieve

    Returns
    -------
        A pandas Dataframe

    """
    return _client_instance().load(name=name, snapshot=snapshot, limit=limit, ids=ids)


def delete(name: str) -> None:
    """
    Delete a dataset with given name

    Parameters
    ----------
    name:
        The dataset name

    """
    _client_instance().delete(name=name)
