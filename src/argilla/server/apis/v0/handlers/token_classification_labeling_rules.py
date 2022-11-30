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

from argilla.server.apis.v0.models.commons.model import BaseUpdateLabelingRule
from argilla.server.apis.v0.models.commons.params import CommonTaskHandlerDependencies
from argilla.server.commons.config import TasksFactory
from argilla.server.commons.models import TaskType
from argilla.server.security import auth
from argilla.server.security.model import User
from argilla.server.services.datasets import DatasetsService
from argilla.server.services.tasks.token_classification import (
    TokenClassificationService,
)
from argilla.server.services.tasks.token_classification.labeling_rules.service import (
    RuleRecordInfo,
    ServiceLabelingRule,
)


class UpdateLabelingRule(BaseUpdateLabelingRule):
    label: Optional[str] = Field(
        default=None,
        description="The label associated with the rule.",
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


class SearchRecordsByRuleRequest(BaseModel):
    record_ids: List[str]


class RecordRuleAnnotations(BaseModel):
    total: int
    agent: str
    records: List[RuleRecordInfo] = Field(default_factory=list)
    next: Optional[str] = Field(
        None,
        description="User to paginate results. "
        "Provide this value in a search request to fetch next chunk of annotations",
    )


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
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        service: TokenClassificationService = Depends(
            TokenClassificationService.get_instance
        ),
    ) -> List[LabelingRule]:

        dataset = datasets.find_by_name(
            user=current_user,
            name=name,
            task=task,
            workspace=common_params.workspace,
            as_dataset_class=TasksFactory.get_task_dataset(task),
        )

        return [
            LabelingRule.parse_obj(rule) for rule in service.get_labeling_rules(dataset)
        ]

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
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        service: TokenClassificationService = Depends(
            TokenClassificationService.get_instance
        ),
    ) -> LabelingRule:

        dataset = datasets.find_by_name(
            user=current_user,
            name=name,
            task=task,
            workspace=common_params.workspace,
            as_dataset_class=TasksFactory.get_task_dataset(task),
        )

        rule = ServiceLabelingRule(
            **rule.dict(),
            author=current_user.username,
        )
        service.add_labeling_rule(
            dataset,
            rule=rule,
        )
        return LabelingRule.parse_obj(rule)

    @router.post(
        path=f"{base_endpoint}/{{query_or_name:path}}/annotations",
        operation_id="search_rule_records",
        description="Fetch matched record annotations by the provided rule",
        response_model=RecordRuleAnnotations,
        response_model_exclude_none=True,
    )
    async def fetch_rule_annotations(
        name: str,
        query_or_name: str,
        request: Optional[SearchRecordsByRuleRequest] = None,
        label: Optional[str] = Query(
            None,
            description="Label related to query rule",
        ),
        common_params: CommonTaskHandlerDependencies = Depends(),
        current_user: User = Security(auth.get_user, scopes=[]),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        service: TokenClassificationService = Depends(
            TokenClassificationService.get_instance
        ),
    ) -> RecordRuleAnnotations:

        dataset = datasets.find_by_name(
            user=current_user,
            name=name,
            task=task,
            workspace=common_params.workspace,
            as_dataset_class=TasksFactory.get_task_dataset(task),
        )

        total, rule_name, records = service.search_by_rule(
            dataset=dataset,
            query=query_or_name,
            record_ids=request.record_ids if request else None,
            label=label,
        )

        return RecordRuleAnnotations(
            records=records,
            agent=rule_name,
            total=total,
        )

    @router.get(
        path=f"{base_endpoint}/summary",
        operation_id="compute_dataset_rules_metrics",
        description="Computes overall metrics for dataset labeling rules",
        response_model=DatasetLabelingRulesMetricsSummary,
        response_model_exclude_none=True,
    )
    async def compute_dataset_rules_metrics(
        name: str,
        common_params: CommonTaskHandlerDependencies = Depends(),
        current_user: User = Security(auth.get_user, scopes=[]),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        service: TokenClassificationService = Depends(
            TokenClassificationService.get_instance
        ),
    ) -> DatasetLabelingRulesMetricsSummary:

        dataset = datasets.find_by_name(
            user=current_user,
            name=name,
            task=task,
            workspace=common_params.workspace,
            as_dataset_class=TasksFactory.get_task_dataset(task),
        )

        total, annotated, summary = service.compute_dataset_rules_summary(
            dataset=dataset
        )
        return DatasetLabelingRulesMetricsSummary(
            coverage=summary.covered_records,
            coverage_annotated=summary.annotated_covered_records,
            annotated_records=annotated,
            total_records=total,
        )

    @router.get(
        path=f"{base_endpoint}/{{query_or_name:path}}/summary",
        operation_id="compute_rule_metrics",
        description="Computes dataset labeling rule metrics",
        response_model=LabelingRuleSearchResults,
        response_model_exclude_none=True,
    )
    async def compute_rule_metrics(
        name: str,
        query_or_name: str,
        label: Optional[str] = Query(
            None,
            description="Label related to query rule",
        ),
        common_params: CommonTaskHandlerDependencies = Depends(),
        current_user: User = Security(auth.get_user, scopes=[]),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        service: TokenClassificationService = Depends(
            TokenClassificationService.get_instance
        ),
    ) -> LabelingRuleSearchResults:

        dataset = datasets.find_by_name(
            user=current_user,
            name=name,
            task=task,
            workspace=common_params.workspace,
            as_dataset_class=TasksFactory.get_task_dataset(task),
        )

        total_records, annotated_records, summary = service.compute_rule_summary(
            dataset=dataset,
            rule_query=query_or_name,
        )
        response = LabelingRuleSearchResults(
            coverage=summary.covered_records / total_records if total_records else 0.0,
            coverage_annotated=summary.annotated_covered_records / annotated_records
            if annotated_records
            else 0.0,
            total_records=total_records,
            annotated_records=annotated_records,
        )

        return response

    @router.delete(
        path=f"{base_endpoint}/{{query_or_name:path}}",
        operation_id="delete_labeling_rule",
        description="Deletes a labeling rule from dataset",
    )
    async def delete_labeling_rule(
        name: str,
        query_or_name: str,
        common_params: CommonTaskHandlerDependencies = Depends(),
        current_user: User = Security(auth.get_user, scopes=[]),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        service: TokenClassificationService = Depends(
            TokenClassificationService.get_instance
        ),
    ) -> None:
        dataset = datasets.find_by_name(
            user=current_user,
            name=name,
            task=task,
            workspace=common_params.workspace,
            as_dataset_class=TasksFactory.get_task_dataset(task),
        )

        service.delete_labeling_rule(dataset, rule_query=query_or_name)

    @router.get(
        path=f"{base_endpoint}/{{query_or_name:path}}",
        operation_id="get_rule",
        description="Get the dataset labeling rule",
        response_model=LabelingRule,
        response_model_exclude_none=True,
    )
    async def get_rule(
        name: str,
        query_or_name: str,
        common_params: CommonTaskHandlerDependencies = Depends(),
        current_user: User = Security(auth.get_user, scopes=[]),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        service: TokenClassificationService = Depends(
            TokenClassificationService.get_instance
        ),
    ) -> LabelingRule:

        dataset = datasets.find_by_name(
            user=current_user,
            name=name,
            task=task,
            workspace=common_params.workspace,
            as_dataset_class=TasksFactory.get_task_dataset(task),
        )
        rule = service.find_labeling_rule(
            dataset,
            query_or_name=query_or_name,
        )
        return LabelingRule.parse_obj(rule)

    @router.patch(
        path=f"{base_endpoint}/{{query_or_name:path}}",
        operation_id="update_rule",
        description="Update dataset labeling rule attributes",
        response_model=LabelingRule,
        response_model_exclude_none=True,
    )
    async def update_rule(
        name: str,
        query_or_name: str,
        update: UpdateLabelingRule,
        common_params: CommonTaskHandlerDependencies = Depends(),
        current_user: User = Security(auth.get_user, scopes=[]),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        service: TokenClassificationService = Depends(
            TokenClassificationService.get_instance
        ),
    ) -> LabelingRule:
        dataset = datasets.find_by_name(
            user=current_user,
            name=name,
            task=task,
            workspace=common_params.workspace,
            as_dataset_class=TasksFactory.get_task_dataset(task),
        )

        params = {"label": update.label} if update.label else {}
        rule = service.update_labeling_rule(
            dataset,
            query_or_name=query_or_name,
            description=update.description,
            name=update.name,
            **params,
        )

        return LabelingRule.parse_obj(rule)
