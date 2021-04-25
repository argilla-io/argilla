from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RecordSearch(BaseModel):
    """
    Dao search

    Attributes:
    -----------

    query:
        The elasticsearch search query portion

    aggregations:
        The elasticsearch search aggregations
    """

    query: Optional[Dict[str, Any]]
    aggregations: Optional[Dict[str, Any]]


class RecordSearchResults(BaseModel):
    """
    Dao search results

    Attributes:
    -----------

    total: int
        The total of query results
    records: List[T]
        List of records retrieved for the pagination configuration
    aggregations: Optional[Dict[str, Dict[str, Any]]]
        The query aggregations grouped by task. Optional
    words: Optional[Dict[str, int]]
        The words cloud aggregations
    metadata: Optional[Dict[str, int]]
        Metadata fields aggregations
    """

    total: int
    records: List[Dict[str, Any]]
    aggregations: Optional[Dict[str, Dict[str, Any]]] = Field(default_factory=dict)
    words: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, int]] = None
