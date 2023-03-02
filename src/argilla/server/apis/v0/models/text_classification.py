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
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, root_validator, validator

from argilla.server.apis.v0.models.commons.model import (
    BaseRecord,
    BaseRecordInputs,
    BaseSearchResults,
    ScoreRange,
    SortableField,
)
from argilla.server.commons.models import PredictionStatus
from argilla.server.schemas.datasets import UpdateDatasetRequest
from argilla.server.services.search.model import (
    ServiceBaseRecordsQuery,
    ServiceBaseSearchResultsAggregations,
)
from argilla.server.services.tasks.text_classification.model import (
    DatasetLabelingRulesMetricsSummary as _DatasetLabelingRulesMetricsSummary,
)
from argilla.server.services.tasks.text_classification.model import (
    LabelingRuleMetricsSummary as _LabelingRuleMetricsSummary,
)
from argilla.server.services.tasks.text_classification.model import (
    ServiceTextClassificationDataset,
    TokenAttributions,
)
from argilla.server.services.tasks.text_classification.model import (
    TextClassificationAnnotation as _TextClassificationAnnotation,
)


class UpdateLabelingRule(BaseModel):
    label: Optional[str] = Field(default=None, description="@Deprecated::The label associated with the rule.")
    labels: List[str] = Field(
        default_factory=list,
        description="For multi label problems, a list of labels. " "It will replace the `label` field",
    )
    description: Optional[str] = Field(None, description="A brief description of the rule")

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
    query: str = Field(description="The es rule query")

    @validator("query")
    def strip_query(cls, query: str) -> str:
        """Remove blank spaces for query"""
        return query.strip()


class LabelingRule(CreateLabelingRule):
    author: str = Field(description="User who created the rule")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Rule creation timestamp")


class LabelingRuleMetricsSummary(_LabelingRuleMetricsSummary):
    pass


class DatasetLabelingRulesMetricsSummary(_DatasetLabelingRulesMetricsSummary):
    pass


class TextClassificationDataset(ServiceTextClassificationDataset):
    pass


class TextClassificationAnnotation(_TextClassificationAnnotation):
    pass


class TextClassificationRecordInputs(BaseRecordInputs[TextClassificationAnnotation]):
    inputs: Dict[str, Union[str, List[str]]]
    multi_label: bool = False
    explanation: Optional[Dict[str, List[TokenAttributions]]] = None


class TextClassificationRecord(TextClassificationRecordInputs, BaseRecord[TextClassificationAnnotation]):
    pass


class TextClassificationBulkRequest(UpdateDatasetRequest):
    records: List[TextClassificationRecordInputs]

    @validator("records")
    def check_multi_label_integrity(cls, records: List[TextClassificationRecord]):
        """Checks all records in batch have same multi-label configuration"""
        if records:
            multi_label = records[0].multi_label
            for record in records[1:]:
                assert multi_label == record.multi_label, "All records must be single/multi labelled"
        return records


class TextClassificationQuery(ServiceBaseRecordsQuery):
    predicted_as: List[str] = Field(default_factory=list)
    annotated_as: List[str] = Field(default_factory=list)
    score: Optional[ScoreRange] = Field(default=None)
    predicted: Optional[PredictionStatus] = Field(default=None, nullable=True)

    uncovered_by_rules: List[str] = Field(
        default_factory=list,
        description="List of rule queries that WILL NOT cover the resulting records",
    )


class TextClassificationSearchAggregations(ServiceBaseSearchResultsAggregations):
    pass


class TextClassificationSearchResults(
    BaseSearchResults[TextClassificationRecord, TextClassificationSearchAggregations]
):
    pass


class TextClassificationSearchRequest(BaseModel):
    query: TextClassificationQuery = Field(default_factory=TextClassificationQuery)
    sort: List[SortableField] = Field(default_factory=list)
