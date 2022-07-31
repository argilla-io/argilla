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

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, root_validator, validator

from rubrix.server.apis.v0.models.commons.model import SortableField
from rubrix.server.apis.v0.models.datasets import UpdateDatasetRequest
from rubrix.server.services.tasks.text_classification.model import (
    CreationTextClassificationRecord as _CreationTextClassificationRecord,
)
from rubrix.server.services.tasks.text_classification.model import (
    DatasetLabelingRulesMetricsSummary as _DatasetLabelingRulesMetricsSummary,
)
from rubrix.server.services.tasks.text_classification.model import (
    TextClassificationAnnotation as _TextClassificationAnnotation,
)
from rubrix.server.services.tasks.text_classification.model import (
    TextClassificationDatasetDB as _TextClassificationDatasetDB,
)
from rubrix.server.services.tasks.text_classification.model import (
    TextClassificationQuery as _TextClassificationQuery,
)
from rubrix.server.services.tasks.text_classification.model import (
    TextClassificationRecord as _TextClassificationRecord,
)
from rubrix.server.services.tasks.text_classification.model import (
    TextClassificationRecordDB as _TextClassificationRecordDB,
)
from rubrix.server.services.tasks.text_classification.model import (
    TextClassificationSearchAggregations as _TextClassificationSearchAggregations,
)
from rubrix.server.services.tasks.text_classification.model import (
    TextClassificationSearchResults as _TextClassificationSearchResults,
)


class UpdateLabelingRule(BaseModel):
    label: Optional[str] = Field(
        default=None, description="@Deprecated::The label associated with the rule."
    )
    labels: List[str] = Field(
        default_factory=list,
        description="For multi label problems, a list of labels. "
        "It will replace the `label` field",
    )
    description: Optional[str] = Field(
        None, description="A brief description of the rule"
    )

    @root_validator
    def initialize_labels(cls, values):
        label = values.get("label", None)
        labels = values.get("labels", [])

        if label:
            labels.append(label)
            values["labels"] = list(set(labels))

        assert len(labels) >= 1, f"No labels was provided in rule {values}"
        return values


class CreateLabelingRule(UpdateLabelingRule):
    """
    Data model for labeling rules creation

    Attributes:
    -----------

    query:
        The ES query of the rule

    label: str
        The label associated with the rule

    description:
        A brief description of the rule

    """

    query: str = Field(description="The es rule query")

    @validator("query")
    def strip_query(cls, query: str) -> str:
        """Remove blank spaces for query"""
        return query.strip()


class LabelingRule(CreateLabelingRule):
    """
    Adds read-only attributes to the labeling rule

    Attributes:
    -----------

    author:
        Who created the rule

    created_at:
        When was the rule created

    """

    author: str = Field(description="User who created the rule")
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow, description="Rule creation timestamp"
    )


class LabelingRuleMetricsSummary(BaseModel):
    """Metrics generated for a labeling rule"""

    coverage: Optional[float] = None
    coverage_annotated: Optional[float] = None
    correct: Optional[float] = None
    incorrect: Optional[float] = None
    precision: Optional[float] = None

    total_records: int
    annotated_records: int


class DatasetLabelingRulesMetricsSummary(_DatasetLabelingRulesMetricsSummary):
    pass


class TextClassificationDatasetDB(_TextClassificationDatasetDB):
    pass


class TextClassificationAnnotation(_TextClassificationAnnotation):
    pass


class CreationTextClassificationRecord(_CreationTextClassificationRecord):
    pass


class TextClassificationRecordDB(_TextClassificationRecordDB):
    pass


class TextClassificationRecord(_TextClassificationRecord):
    pass


class TextClassificationBulkData(UpdateDatasetRequest):
    """
    API bulk data for text classification

    Attributes:
    -----------

    records: List[CreationTextClassificationRecord]
        The text classification record list

    """

    records: List[CreationTextClassificationRecord]

    @validator("records")
    def check_multi_label_integrity(cls, records: List[TextClassificationRecord]):
        """Checks all records in batch have same multi-label configuration"""
        if records:
            multi_label = records[0].multi_label
            for record in records[1:]:
                assert (
                    multi_label == record.multi_label
                ), "All records must be single/multi labelled"
        return records


class TextClassificationQuery(_TextClassificationQuery):
    pass


class TextClassificationSearchRequest(BaseModel):
    """
    API SearchRequest request

    Attributes:
    -----------

    query: TextClassificationQuery
        The search query configuration

    sort:
        The sort order list
    """

    query: TextClassificationQuery = Field(default_factory=TextClassificationQuery)
    sort: List[SortableField] = Field(default_factory=list)


class TextClassificationSearchAggregations(_TextClassificationSearchAggregations):
    pass


class TextClassificationSearchResults(_TextClassificationSearchResults):
    pass
