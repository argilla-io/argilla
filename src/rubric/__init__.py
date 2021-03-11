# -*- coding: utf-8 -*-

"""Rubric Init Method

Contains methods for accesing the API.
"""

import logging
from typing import Any, Dict, Iterable, Optional

import pkg_resources
from rubric.client import RubricClient
from rubric.sdk.models import *

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    # package is not installed
    pass

_LOGGER = logging.getLogger(__name__)

_client: Optional[
    RubricClient
] = None  # Client will be stored here to pass it through functions
# TODO: Convert to enviroment variables


def init(
    api_url: str = "http://localhost:8000",
    token: Optional[str] = None,
    timeout: int = 5,
):
    """Client setup function.

    Calling the RubricClient init function

    Parameters
    ----------
    api_url : str
        Address from which the API is serving. It will use the default UVICORN address as default
    token : str
        Authentification token. A non-secured logging will be considered the default case. Optional
    timeout : int
        Seconds to considered a connection timeout. Optional
    """

    global _client

    _client = RubricClient(api_url=api_url, token=token, timeout=timeout)


def log(
    records: Iterable[Any],
    name: str,
    tags: Optional[Dict[str, str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    chunk_size: int = 500,
):
    """
    Register a set of logs into rubric

    Parameters
    ----------
    records:
        The data records list.
    name:
        The dataset name
    tags:
        A set of tags related to dataset. Optional
    metadata:
        A set of extra info for dataset. Optional
    chunk_size:
        The default chunk size for data bulk

    """
    global _client

    # Calling a by-default-init if it was not called before
    if _client is None:
        _LOGGER.warning(
            "Tried to log data without previous initialization. An initialization by default has been performed."
        )
        _client = RubricClient()

    return _client.log(
        records=records, name=name, tags=tags, metadata=metadata, chunk_size=chunk_size
    )
