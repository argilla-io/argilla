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

from fastapi import APIRouter, Depends, Query, Security
from pydantic import BaseModel, Field, validator

from argilla.server.apis.v0.models.commons.params import CommonTaskHandlerDependencies
from argilla.server.apis.v0.models.token_classification import (
    TokenClassificationAnnotation,
    TokenClassificationRecord,
    TokenClassificationSearchResults,
)
from argilla.server.commons.models import TaskType
from argilla.server.errors import EntityNotFoundError
from argilla.server.security import auth
from argilla.server.security.model import User


class UpdateLabelingRule(BaseModel):
    label: str = Field(description="The label associated with the rule.")
    labeling_function: str = Field(description="The labeling function descriptor id")
    description: Optional[str] = Field(
        default=None,
        description="A brief description of the rule",
    )


class CreateLabelingRule(UpdateLabelingRule):
    query: str = Field(description="The rule query")

    @validator("query")
    def strip_query(cls, query: str) -> str:
        """Remove blank spaces for query"""
        return query.strip()


class LabelingRule(CreateLabelingRule):
    author: str = Field(description="User who created the rule")
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow, description="Rule creation timestamp"
    )


class LabelingRuleSearchResults(BaseModel):
    """Metrics generated for a labeling rule"""

    coverage: Optional[float] = None
    coverage_annotated: Optional[float] = None

    total_records: int
    annotated_records: int


class DatasetLabelingRulesMetricsSummary(BaseModel):
    coverage: Optional[float] = None
    coverage_annotated: Optional[float] = None

    total_records: int
    annotated_records: int


def configure_router(router: APIRouter):
    task = TaskType.token_classification
    base_endpoint = f"/{{name}}/{task}/labeling/rules"

    mocked_rules = []

    @router.get(
        path=f"{base_endpoint}",
        operation_id="list_labeling_rules",
        description="List all dataset labeling rules",
        response_model=List[LabelingRule],
        response_model_exclude_none=True,
    )
    async def list_labeling_rules(
        name: str,
        common_params: CommonTaskHandlerDependencies = Depends(),
        current_user: User = Security(auth.get_user, scopes=[]),
    ) -> List[LabelingRule]:

        return mocked_rules

    @router.post(
        path=f"{base_endpoint}",
        operation_id="create_rule",
        description="Creates a new dataset labeling rule",
        response_model=LabelingRule,
        response_model_exclude_none=True,
    )
    async def create_rule(
        name: str,
        rule: CreateLabelingRule,
        common_params: CommonTaskHandlerDependencies = Depends(),
        current_user: User = Security(auth.get_user, scopes=[]),
    ) -> LabelingRule:

        rule = LabelingRule(
            **rule.dict(exclude_none=True),
            author=current_user.username,
            created_at=datetime.utcnow(),
        )

        mocked_rules.append(rule)
        return rule

    @router.get(
        path=f"{base_endpoint}/{{query:path}}:summary",
        operation_id="compute_rule_metrics",
        description="Computes dataset labeling rule metrics",
        response_model=LabelingRuleSearchResults,
        response_model_exclude_none=True,
    )
    async def compute_rule_metrics(
        name: str,
        query: str,
        label: Optional[str] = Query(
            None,
            description="Label related to query rule",
        ),
        common_params: CommonTaskHandlerDependencies = Depends(),
        current_user: User = Security(auth.get_user, scopes=[]),
    ) -> LabelingRuleSearchResults:

        return LabelingRuleSearchResults(
            coverage=56,
            coverage_annotated=12,
            total_records=100,
            annotated_records=30,
        )

    @router.get(
        path=f"{base_endpoint}/{{query:path}}:search",
        operation_id="search_rule_records",
        description="Fetch matched records by the provided rule applying the rule labeling function",
        response_model=TokenClassificationSearchResults,
        response_model_exclude_none=True,
    )
    async def search_rule_records(
        name: str,
        query: str,
        label: Optional[str] = Query(
            None,
            description="Label related to query rule",
        ),
        labeling_function: Optional[str] = Query(
            None, description="Labeling function related to the query rule"
        ),
        common_params: CommonTaskHandlerDependencies = Depends(),
        current_user: User = Security(auth.get_user, scopes=[]),
    ) -> TokenClassificationSearchResults:

        matched_rule = None
        for rule in mocked_rules:
            if rule.query == rule:
                matched_rule = rule
                break
        if not matched_rule:
            matched_rule = CreateLabelingRule(
                query=query,
                label=label,
                labeling_function=labeling_function,
            )
        text = "what do you think?"
        return TokenClassificationSearchResults(
            total=1,
            records=[
                TokenClassificationRecord(
                    text=text,
                    tokens=text.split(" "),
                    annotations={
                        labeling_function: TokenClassificationAnnotation.parse_obj(
                            {
                                "entities": [
                                    {
                                        "start": 0,
                                        "end": 4,
                                        "label": label,
                                    }
                                ]
                            }
                        )
                    },
                )
            ],
        )

    @router.get(
        path=f"{base_endpoint}:summary",
        operation_id="compute_dataset_rules_metrics",
        description="Computes overall metrics for dataset labeling rules",
        response_model=DatasetLabelingRulesMetricsSummary,
        response_model_exclude_none=True,
    )
    async def compute_dataset_rules_metrics(
        name: str,
        common_params: CommonTaskHandlerDependencies = Depends(),
        current_user: User = Security(auth.get_user, scopes=[]),
    ) -> DatasetLabelingRulesMetricsSummary:
        return DatasetLabelingRulesMetricsSummary(
            coverage=73,
            coverage_annotated=22,
            total_records=100,
            annotated_records=30,
        )

    @router.delete(
        path=f"{base_endpoint}/{{query:path}}",
        operation_id="delete_labeling_rule",
        description="Deletes a labeling rule from dataset",
    )
    async def delete_labeling_rule(
        name: str,
        query: str,
        common_params: CommonTaskHandlerDependencies = Depends(),
        current_user: User = Security(auth.get_user, scopes=[]),
    ) -> None:

        for rule_ in mocked_rules:
            if query == rule_.query:
                mocked_rules.remove(rule_)
                break
        raise EntityNotFoundError(name=query, type=LabelingRule)

    @router.get(
        path=f"{base_endpoint}/{{query:path}}",
        operation_id="get_rule",
        description="Get the dataset labeling rule",
        response_model=LabelingRule,
        response_model_exclude_none=True,
    )
    async def get_rule(
        name: str,
        query: str,
        common_params: CommonTaskHandlerDependencies = Depends(),
        current_user: User = Security(auth.get_user, scopes=[]),
    ) -> LabelingRule:
        for rule in mocked_rules:
            if rule.query == query:
                return rule
        raise EntityNotFoundError(name=query, type=LabelingRule)

    @router.patch(
        path=f"{base_endpoint}/{{query:path}}",
        operation_id="update_rule",
        description="Update dataset labeling rule attributes",
        response_model=LabelingRule,
        response_model_exclude_none=True,
    )
    async def update_rule(
        name: str,
        query: str,
        update: UpdateLabelingRule,
        common_params: CommonTaskHandlerDependencies = Depends(),
        current_user: User = Security(auth.get_user, scopes=[]),
    ) -> LabelingRule:
        for rule in mocked_rules:
            if rule.query == query:
                rule.label = update.label
                rule.labeling_function = update.labeling_function
                rule.description = update.description
                return rule

        raise EntityNotFoundError(name=query, type=LabelingRule)
