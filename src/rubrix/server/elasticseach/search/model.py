from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from rubrix.server.commons.models import TaskStatus


class BaseSearchQuery(BaseModel):

    query_text: Optional[str] = None
    advanced_query_dsl: bool = False

    ids: Optional[List[Union[str, int]]]

    annotated_by: List[str] = Field(default_factory=list)
    predicted_by: List[str] = Field(default_factory=list)

    status: List[TaskStatus] = Field(default_factory=list)
    metadata: Optional[Dict[str, Union[str, List[str]]]] = None

    has_annotation: Optional[bool] = None
    has_prediction: Optional[bool] = None
