from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field
from rubrix.server.commons.models import (
    SortParam,
)
from rubrix.server.datasets.model import UpdateDatasetRequest

from .model import TextClassificationRecord
from .task_meta import TaskSearchAggregations, TaskSearchFilters


class TextClassificationBulkData(UpdateDatasetRequest):
    """
    API bulk data for text classification

    Attributes:
    -----------

    records: List[TextClassificationRecord]
        The text classification record list

    """

    records: List[TextClassificationRecord]


class TextClassificationQuery(TaskSearchFilters):
    """
    API Filters for text classification

    Attributes:
    -----------

    text_query: Union[str, Dict[str, str]]
        Text query over inputs

    metadata: Optional[Dict[str, Union[str, List[str]]]]
        Text query over metadata fields. Default=None

    multi_label: Optional[bool]
        Filter by multi label. Default=None

    """

    text_query: Union[str, Dict[str, str]] = Field(
        default_factory=dict, alias="query_inputs"
    )
    metadata: Optional[Dict[str, Union[str, List[str]]]] = None
    multi_label: Optional[bool] = None  # Deprecated


class TextClassificationAggregations(TaskSearchAggregations):
    """
    API for result aggregations

    Attributes:
    -----------

    words: WordCloudAggregations
        The word cloud aggregations (grouped by lang)

    metadata: Dict[str, Dict[str, int]]
        The metadata fields aggregations

    """

    words: Dict[str, int] = Field(default_factory=dict)
    metadata: Dict[str, Dict[str, int]] = Field(default_factory=dict)


class TextClassificationSearchRequest(BaseModel):
    """
    API Search request

    Attributes:
    -----------

    query: TextClassificationQuery
        The search query configuration

    sort: List[SortParam]
        The sort params to use for record results

    """

    query: TextClassificationQuery = Field(default_factory=TextClassificationQuery)
    sort: List[SortParam] = Field(default_factory=list)


class TextClassificationSearchResults(BaseModel):
    """
    API search results

    Attributes:
    -----------

    total: int
        The total number of records
    records: List[TextClassificationRecord]
        The selected records to return
    aggregations: TextClassificationAggregations
        Search aggregations (if no pagination)

    """

    total: int = 0
    records: List[TextClassificationRecord] = Field(default_factory=list)
    aggregations: TextClassificationAggregations = None
