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

import itertools
from typing import Iterable, List, Optional

from fastapi import APIRouter, Depends, Query, Security
from fastapi.responses import StreamingResponse

from argilla.server.apis.v0.handlers import (
    metrics,
    text_classification_dataset_settings,
)
from argilla.server.apis.v0.helpers import deprecate_endpoint
from argilla.server.apis.v0.models.commons.model import BulkResponse
from argilla.server.apis.v0.models.commons.params import (
    CommonTaskHandlerDependencies,
    RequestPagination,
)
from argilla.server.apis.v0.models.text_classification import (
    CreateLabelingRule,
    DatasetLabelingRulesMetricsSummary,
    LabelingRule,
    LabelingRuleMetricsSummary,
    TextClassificationBulkRequest,
    TextClassificationDataset,
    TextClassificationQuery,
    TextClassificationRecord,
    TextClassificationSearchAggregations,
    TextClassificationSearchRequest,
    TextClassificationSearchResults,
    UpdateLabelingRule,
)
from argilla.server.apis.v0.validators.text_classification import DatasetValidator
from argilla.server.commons.config import TasksFactory
from argilla.server.commons.models import TaskType
from argilla.server.errors import EntityNotFoundError
from argilla.server.models import User
from argilla.server.schemas.datasets import CreateDatasetRequest
from argilla.server.security import auth
from argilla.server.services.datasets import DatasetsService
from argilla.server.services.tasks.text_classification import TextClassificationService
from argilla.server.services.tasks.text_classification.metrics import (
    TextClassificationMetrics,
)
from argilla.server.services.tasks.text_classification.model import (
    ServiceLabelingRule,
    ServiceTextClassificationQuery,
    ServiceTextClassificationRecord,
)


def configure_router():
    task_type = TaskType.text_classification

    TasksFactory.register_task(
        task_type=task_type,
        dataset_class=TextClassificationDataset,
        query_request=TextClassificationQuery,
        record_class=ServiceTextClassificationRecord,
        metrics=TextClassificationMetrics,
    )

    base_endpoint = f"/{{name}}/{task_type}"
    new_base_endpoint = f"/{task_type}/{{name}}"

    router = APIRouter(tags=[task_type], prefix="/datasets")

    @router.post(
        f"{base_endpoint}:bulk",
        operation_id="bulk_records",
        response_model=BulkResponse,
        response_model_exclude_none=True,
    )
    async def bulk_records(
        name: str,
        bulk: TextClassificationBulkRequest,
        common_params: CommonTaskHandlerDependencies = Depends(),
        service: TextClassificationService = Depends(TextClassificationService.get_instance),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        validator: DatasetValidator = Depends(DatasetValidator.get_instance),
        current_user: User = Security(auth.get_current_user),
    ) -> BulkResponse:
        task = task_type
        workspace = common_params.workspace
        try:
            dataset = datasets.find_by_name(
                current_user,
                name=name,
                task=task,
                workspace=workspace,
            )
            dataset = datasets.update(
                user=current_user,
                dataset=dataset,
                tags=bulk.tags,
                metadata=bulk.metadata,
            )
        except EntityNotFoundError:
            dataset = CreateDatasetRequest(name=name, workspace=workspace, task=task, **bulk.dict())
            dataset = datasets.create_dataset(user=current_user, dataset=dataset)

        # TODO(@frascuchon): Validator should be applied in the service layer
        records = [ServiceTextClassificationRecord.parse_obj(r) for r in bulk.records]
        await validator.validate_dataset_records(user=current_user, dataset=dataset, records=records)

        result = await service.add_records(
            dataset=dataset,
            records=records,
        )
        return BulkResponse(
            dataset=name,
            processed=result.processed,
            failed=result.failed,
        )

    @router.post(
        f"{base_endpoint}:search",
        response_model=TextClassificationSearchResults,
        response_model_exclude_none=True,
        operation_id="search_records",
    )
    def search_records(
        name: str,
        search: TextClassificationSearchRequest = None,
        common_params: CommonTaskHandlerDependencies = Depends(),
        include_metrics: bool = Query(False, description="If enabled, return related record metrics"),
        pagination: RequestPagination = Depends(),
        service: TextClassificationService = Depends(TextClassificationService.get_instance),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        current_user: User = Security(auth.get_current_user),
    ) -> TextClassificationSearchResults:
        """
        Searches data from dataset

        Parameters
        ----------
        name:
            The dataset name
        search:
            The search query request
        common_params:
            Common query params
        include_metrics:
            Flag to enable include metrics
        pagination:
            The pagination params
        service:
            The dataset records service
        datasets:
            The dataset service
        current_user:
            The current request user


        Returns
        -------
            The search results data

        """

        search = search or TextClassificationSearchRequest()
        query = search.query or TextClassificationQuery()
        dataset = datasets.find_by_name(
            user=current_user,
            name=name,
            task=task_type,
            workspace=common_params.workspace,
        )
        result = service.search(
            dataset=dataset,
            query=ServiceTextClassificationQuery.parse_obj(query),
            sort_by=search.sort,
            record_from=pagination.from_,
            size=pagination.limit,
            exclude_metrics=not include_metrics,
        )

        return TextClassificationSearchResults(
            total=result.total,
            records=result.records,
            aggregations=TextClassificationSearchAggregations.parse_obj(result.metrics) if result.metrics else None,
        )

    @deprecate_endpoint(
        path=f"{new_base_endpoint}/labeling/rules",
        new_path=f"{base_endpoint}/labeling/rules",
        router_method=router.get,
        operation_id="list_labeling_rules",
        description="List all dataset labeling rules",
        response_model=List[LabelingRule],
        response_model_exclude_none=True,
    )
    async def list_labeling_rules(
        name: str,
        common_params: CommonTaskHandlerDependencies = Depends(),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        service: TextClassificationService = Depends(TextClassificationService.get_instance),
        current_user: User = Security(auth.get_current_user),
    ) -> List[LabelingRule]:
        dataset = datasets.find_by_name(
            user=current_user,
            name=name,
            task=task_type,
            workspace=common_params.workspace,
            as_dataset_class=TextClassificationDataset,
        )

        return [LabelingRule.parse_obj(rule) for rule in service.list_labeling_rules(dataset)]

    @deprecate_endpoint(
        path=f"{new_base_endpoint}/labeling/rules",
        new_path=f"{base_endpoint}/labeling/rules",
        router_method=router.post,
        operation_id="create_rule",
        description="Creates a new dataset labeling rule",
        response_model=LabelingRule,
        response_model_exclude_none=True,
    )
    async def create_rule(
        name: str,
        rule: CreateLabelingRule,
        common_params: CommonTaskHandlerDependencies = Depends(),
        service: TextClassificationService = Depends(TextClassificationService.get_instance),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        current_user: User = Security(auth.get_current_user),
    ) -> LabelingRule:
        dataset = datasets.find_by_name(
            user=current_user,
            name=name,
            task=task_type,
            workspace=common_params.workspace,
            as_dataset_class=TextClassificationDataset,
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

    @deprecate_endpoint(
        path=f"{new_base_endpoint}/labeling/rules/{{query:path}}/metrics",
        new_path=f"{base_endpoint}/labeling/rules/{{query:path}}/metrics",
        router_method=router.get,
        operation_id="compute_rule_metrics",
        description="Computes dataset labeling rule metrics",
        response_model=LabelingRuleMetricsSummary,
        response_model_exclude_none=True,
    )
    async def compute_rule_metrics(
        name: str,
        query: str,
        labels: Optional[List[str]] = Query(None, description="Label related to query rule", alias="label"),
        common_params: CommonTaskHandlerDependencies = Depends(),
        service: TextClassificationService = Depends(TextClassificationService.get_instance),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        current_user: User = Security(auth.get_current_user),
    ) -> LabelingRuleMetricsSummary:
        dataset = datasets.find_by_name(
            user=current_user,
            name=name,
            task=task_type,
            workspace=common_params.workspace,
            as_dataset_class=TextClassificationDataset,
        )

        return service.compute_labeling_rule(dataset, rule_query=query, labels=labels)

    @deprecate_endpoint(
        path=f"{new_base_endpoint}/labeling/rules/metrics",
        new_path=f"{base_endpoint}/labeling/rules/metrics",
        router_method=router.get,
        operation_id="compute_dataset_rules_metrics",
        description="Computes overall metrics for dataset labeling rules",
        response_model=DatasetLabelingRulesMetricsSummary,
        response_model_exclude_none=True,
    )
    async def compute_dataset_rules_metrics(
        name: str,
        common_params: CommonTaskHandlerDependencies = Depends(),
        service: TextClassificationService = Depends(TextClassificationService.get_instance),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        current_user: User = Security(auth.get_current_user),
    ) -> DatasetLabelingRulesMetricsSummary:
        dataset = datasets.find_by_name(
            user=current_user,
            name=name,
            task=task_type,
            workspace=common_params.workspace,
            as_dataset_class=TextClassificationDataset,
        )
        metrics = service.compute_all_labeling_rules(dataset)
        return DatasetLabelingRulesMetricsSummary.parse_obj(metrics)

    @deprecate_endpoint(
        path=f"{new_base_endpoint}/labeling/rules/{{query:path}}",
        new_path=f"{base_endpoint}/labeling/rules/{{query:path}}",
        router_method=router.delete,
        operation_id="delete_labeling_rule",
        description="Deletes a labeling rule from dataset",
    )
    async def delete_labeling_rule(
        name: str,
        query: str,
        common_params: CommonTaskHandlerDependencies = Depends(),
        service: TextClassificationService = Depends(TextClassificationService.get_instance),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        current_user: User = Security(auth.get_current_user),
    ) -> None:
        dataset = datasets.find_by_name(
            user=current_user,
            name=name,
            task=task_type,
            workspace=common_params.workspace,
            as_dataset_class=TextClassificationDataset,
        )

        service.delete_labeling_rule(dataset, rule_query=query)

    @deprecate_endpoint(
        path=f"{new_base_endpoint}/labeling/rules/{{query:path}}",
        new_path=f"{base_endpoint}/labeling/rules/{{query:path}}",
        router_method=router.get,
        operation_id="get_rule",
        description="Get the dataset labeling rule",
        response_model=LabelingRule,
        response_model_exclude_none=True,
    )
    async def get_rule(
        name: str,
        query: str,
        common_params: CommonTaskHandlerDependencies = Depends(),
        service: TextClassificationService = Depends(TextClassificationService.get_instance),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        current_user: User = Security(auth.get_current_user),
    ) -> LabelingRule:
        dataset = datasets.find_by_name(
            user=current_user,
            name=name,
            task=task_type,
            workspace=common_params.workspace,
            as_dataset_class=TextClassificationDataset,
        )
        rule = service.find_labeling_rule(dataset, rule_query=query)
        return LabelingRule.parse_obj(rule)

    @deprecate_endpoint(
        path=f"{new_base_endpoint}/labeling/rules/{{query:path}}",
        new_path=f"{base_endpoint}/labeling/rules/{{query:path}}",
        router_method=router.patch,
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
        service: TextClassificationService = Depends(TextClassificationService.get_instance),
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        current_user: User = Security(auth.get_current_user),
    ) -> LabelingRule:
        dataset = datasets.find_by_name(
            user=current_user,
            name=name,
            task=task_type,
            workspace=common_params.workspace,
            as_dataset_class=TextClassificationDataset,
        )

        rule = service.update_labeling_rule(
            dataset,
            rule_query=query,
            labels=update.labels,
            description=update.description,
        )
        return LabelingRule.parse_obj(rule)

    text_classification_dataset_settings.configure_router(router)
    metrics.configure_router(
        router,
        cfg=TasksFactory.get_task_by_task_type(task_type),
    )
    return router


router = configure_router()
