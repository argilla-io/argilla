from typing import List, Optional

from fastapi import APIRouter, Body, Depends, Path, Query, Security

from rubrix.server.api.v1 import API_VERSION
from rubrix.server.api.v1.config.factory import __all__ as all_tasks
from rubrix.server.api.v1.models.commons.params import (
    NameEndpointHandlerParams,
    PaginationParams,
    TaskNameEndpointHandlerParams,
)
from rubrix.server.api.v1.models.weak_supervision import (
    DatasetRules,
    DatasetRulesMetrics,
    RuleMetrics,
)
from rubrix.server.datasets.service import DatasetsService
from rubrix.server.security import auth
from rubrix.server.security.model import User
from rubrix.server.tasks.commons.service import TaskService


def configure_router() -> APIRouter:
    """Configure path routes to router"""
    router = APIRouter(tags=[f"{API_VERSION} / Weak Supervision"])

    for cfg in all_tasks:
        base_endpoint = f"/{cfg.task}/{{name}}/labeling/rules"

        if not (
            cfg.create_rule_class and cfg.update_rule_class and cfg.output_rule_class
        ):
            continue

        dataset_rules_class = type(
            f"DatasetRules_{cfg.task}", (DatasetRules[cfg.output_rule_class],), {}
        )

        @router.get(
            base_endpoint,
            name=f"Get labeling rules for a {cfg.task} dataset",
            response_model=dataset_rules_class,
            response_model_exclude_none=True,
            operation_id=f"{cfg.task}/get_dataset_labeling_rules",
        )
        async def get_dataset_labeling_rules(
            params: NameEndpointHandlerParams = Depends(),
            pagination: PaginationParams = Depends(),
            datasets: DatasetsService = Depends(DatasetsService.get_instance),
            service: TaskService = Depends(cfg.service_class.get_instance),
            user: User = Security(auth.get_user, scopes=["read"]),
        ) -> dataset_rules_class:
            dataset = datasets.find_by_name(
                user=user,
                name=params.name,
                workspace=params.common.workspace,
                task=cfg.task,
            )

            rules = await service.get_labeling_rules(dataset)
            rules = list(rules)

            return dataset_rules_class(total=len(rules), rules=rules)

        @router.post(
            base_endpoint,
            name=f"Create a labeling rule for a {cfg.task} dataset",
            response_model=cfg.output_rule_class,
            response_model_exclude_none=True,
            operation_id=f"{cfg.task}/create_dataset_rule",
        )
        async def create_dataset_rule(
            request: cfg.create_rule_class = Body(...),
            params: NameEndpointHandlerParams = Depends(),
            datasets: DatasetsService = Depends(DatasetsService.get_instance),
            service: TaskService = Depends(cfg.service_class.get_instance),
            user: User = Security(auth.get_user, scopes=["read", "write"]),
        ) -> cfg.output_rule_class:

            dataset = datasets.find_by_name(
                user=user,
                name=params.name,
                workspace=params.common.workspace,
                task=cfg.task,
            )

            created_rule = await service.add_labeling_rule(dataset, rule=request)
            return cfg.output_rule_class.parse_obj(created_rule)

        @router.get(
            f"{base_endpoint}/{{query:path}}",
            name=f"Get a {cfg.task} dataset rule",
            response_model=cfg.output_rule_class,
            response_model_exclude_none=True,
            operation_id=f"{cfg.task}/get_dataset_rule",
        )
        async def get_dataset_rule(
            params: NameEndpointHandlerParams = Depends(),
            query: str = Path(...),
            datasets: DatasetsService = Depends(DatasetsService.get_instance),
            service: TaskService = Depends(cfg.service_class.get_instance),
            user: User = Security(auth.get_user, scopes=["read"]),
        ) -> cfg.output_rule_class:
            dataset = datasets.find_by_name(
                user=user,
                name=params.name,
                workspace=params.common.workspace,
                task=cfg.task,
            )

            rule = await service.find_labeling_rule(dataset, query=query)
            return cfg.output_rule_class.parse_obj(rule)

        "PATCH  /datasets/:task/:name/labeling/rules/:query"  # Partial update of dataset rule

        @router.patch(
            f"{base_endpoint}/{{query:path}}",
            name=f"Update a {cfg.task} rule for a datataset",
            operation_id=f"{cfg.task}/update_dataset_rule",
        )
        async def update_dataset_rule(
            request: cfg.update_rule_class = Body(...),
            params: NameEndpointHandlerParams = Depends(),
            query: str = Path(...),
            datasets: DatasetsService = Depends(DatasetsService.get_instance),
            service: TaskService = Depends(cfg.service_class.get_instance),
            user: User = Security(auth.get_user, scopes=["read", "write"]),
        ) -> cfg.output_rule_class:
            dataset = datasets.find_by_name(
                user=user,
                name=params.name,
                workspace=params.common.workspace,
                task=cfg.task,
            )
            rule = await service.update_labeling_rule(dataset, query, **request.dict())
            return cfg.output_rule_class.parse_obj(rule)

        @router.delete(
            f"{base_endpoint}/{{query:path}}",
            name=f"Delete a {cfg.task} rule from a dataset",
            operation_id=f"{cfg.task}/delete_dataset_rule",
        )
        async def delete_dataset_rule(
            params: NameEndpointHandlerParams = Depends(),
            query: str = Path(...),
            datasets: DatasetsService = Depends(DatasetsService.get_instance),
            service: TaskService = Depends(cfg.service_class.get_instance),
            user: User = Security(auth.get_user, scopes=["read", "admin"]),
        ):
            dataset = datasets.find_by_name(
                user=user,
                name=params.name,
                workspace=params.common.workspace,
                task=cfg.task,
            )

            await service.delete_labeling_rule(dataset, query)

        @router.post(
            f"{base_endpoint}:summary",
            name="Compute overall metrics for dataset rules",
            response_model=DatasetRulesMetrics,
            response_model_exclude_none=True,
            operation_id="dataset_rules_metrics",
        )
        async def dataset_rules_metrics(
            params: NameEndpointHandlerParams = Depends(),
            datasets: DatasetsService = Depends(DatasetsService.get_instance),
            service: TaskService = Depends(cfg.service_class.get_instance),
            user: User = Security(auth.get_user, scopes=["read", "compute"]),
        ) -> DatasetRulesMetrics:

            dataset = datasets.find_by_name(
                user=user,
                name=params.name,
                workspace=params.common.workspace,
                task=cfg.task,
            )

            metrics = service.compute_overall_rules_metrics(dataset)
            return DatasetRulesMetrics.parse_obj(metrics)

        @router.post(
            f"{base_endpoint}/{{query:path}}:summary",
            name="Compute metrics for a given labeling dataset rule",
            response_model=RuleMetrics,
            response_model_exclude_none=True,
            operation_id="dataset_rule_metrics",
        )
        async def dataset_rule_metrics(
            params: TaskNameEndpointHandlerParams = Depends(),
            query: str = Path(...),
            labels: Optional[List[str]] = Query(
                None, description="Label related to query rule", alias="label"
            ),
            datasets: DatasetsService = Depends(DatasetsService.get_instance),
            service: TaskService = Depends(cfg.service_class.get_instance),
            user: User = Security(auth.get_user, scopes=["read", "compute"]),
        ) -> RuleMetrics:

            dataset = datasets.find_by_name(
                user=user,
                name=params.name,
                workspace=params.common.workspace,
                task=params.task,
            )

            metrics = service.compute_rule_metrics(
                dataset,
                query,
                labels=labels,
            )
            return RuleMetrics.parse_obj(metrics)

    return router


__router__ = configure_router()
