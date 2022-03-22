from typing import List, Optional

from fastapi import Depends, Query, Security

from rubrix.server.commons.api import CommonTaskQueryParams
from rubrix.server.datasets.service import DatasetsService
from rubrix.server.security import auth
from rubrix.server.security.model import User
from rubrix.server.tasks.text_classification.api.model import (
    CreateLabelingRule,
    DatasetLabelingRulesMetricsSummary,
    LabelingRule,
    LabelingRuleMetricsSummary,
    UpdateLabelingRule,
)
from rubrix.server.tasks.text_classification.service.service import (
    TextClassificationService,
)

from .api import NEW_BASE_ENDPOINT, TASK_TYPE, router


@router.get(
    f"{NEW_BASE_ENDPOINT}/labeling/rules",
    operation_id="list_labeling_rules",
    description="List all dataset labeling rules",
    response_model=List[LabelingRule],
    response_model_exclude_none=True,
)
async def list_labeling_rules(
    name: str,
    common_params: CommonTaskQueryParams = Depends(),
    datasets: DatasetsService = Depends(DatasetsService.get_instance),
    service: TextClassificationService = Depends(
        TextClassificationService.get_instance
    ),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> List[LabelingRule]:

    dataset = datasets.find_by_name(
        user=current_user,
        name=name,
        task=TASK_TYPE,
        workspace=common_params.workspace,
    )

    return list(service.get_labeling_rules(dataset))


@router.post(
    f"{NEW_BASE_ENDPOINT}/labeling/rules",
    operation_id="create_rule",
    description="Creates a new dataset labeling rule",
    response_model=LabelingRule,
    response_model_exclude_none=True,
)
async def create_rule(
    name: str,
    rule: CreateLabelingRule,
    common_params: CommonTaskQueryParams = Depends(),
    service: TextClassificationService = Depends(
        TextClassificationService.get_instance
    ),
    datasets: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> LabelingRule:

    dataset = datasets.find_by_name(
        user=current_user,
        name=name,
        task=TASK_TYPE,
        workspace=common_params.workspace,
    )

    rule = LabelingRule(
        **rule.dict(),
        author=current_user.username,
    )
    service.add_labeling_rule(
        dataset,
        rule=rule,
    )

    return rule


@router.get(
    f"{NEW_BASE_ENDPOINT}/labeling/rules/{{query}}/metrics",
    operation_id="compute_rule_metrics",
    description="Computes dataset labeling rule metrics",
    response_model=LabelingRuleMetricsSummary,
    response_model_exclude_none=True,
)
async def compute_rule_metrics(
    name: str,
    query: str,
    labels: Optional[List[str]] = Query(
        None, description="Label related to query rule", alias="label"
    ),
    common_params: CommonTaskQueryParams = Depends(),
    service: TextClassificationService = Depends(
        TextClassificationService.get_instance
    ),
    datasets: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> LabelingRuleMetricsSummary:
    dataset = datasets.find_by_name(
        user=current_user,
        name=name,
        task=TASK_TYPE,
        workspace=common_params.workspace,
    )

    return service.compute_rule_metrics(dataset, rule_query=query, labels=labels)


@router.get(
    f"{NEW_BASE_ENDPOINT}/labeling/rules/metrics",
    operation_id="compute_dataset_rules_metrics",
    description="Computes overall metrics for dataset labeling rules",
    response_model=DatasetLabelingRulesMetricsSummary,
    response_model_exclude_none=True,
)
async def compute_dataset_rules_metrics(
    name: str,
    common_params: CommonTaskQueryParams = Depends(),
    service: TextClassificationService = Depends(
        TextClassificationService.get_instance
    ),
    datasets: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> DatasetLabelingRulesMetricsSummary:
    dataset = datasets.find_by_name(
        user=current_user,
        name=name,
        task=TASK_TYPE,
        workspace=common_params.workspace,
    )

    return service.compute_overall_rules_metrics(dataset)


@router.delete(
    f"{NEW_BASE_ENDPOINT}/labeling/rules/{{query}}",
    operation_id="delete_labeling_rule",
    description="Deletes a labeling rule from dataset",
)
async def delete_labeling_rule(
    name: str,
    query: str,
    common_params: CommonTaskQueryParams = Depends(),
    service: TextClassificationService = Depends(
        TextClassificationService.get_instance
    ),
    datasets: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> None:

    dataset = datasets.find_by_name(
        user=current_user,
        name=name,
        task=TASK_TYPE,
        workspace=common_params.workspace,
    )

    service.delete_labeling_rule(dataset, rule_query=query)


@router.get(
    f"{NEW_BASE_ENDPOINT}/labeling/rules/{{query}}",
    operation_id="get_rule",
    description="Get the dataset labeling rule",
    response_model=LabelingRule,
    response_model_exclude_none=True,
)
async def get_rule(
    name: str,
    query: str,
    common_params: CommonTaskQueryParams = Depends(),
    service: TextClassificationService = Depends(
        TextClassificationService.get_instance
    ),
    datasets: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> LabelingRule:

    dataset = datasets.find_by_name(
        user=current_user,
        name=name,
        task=TASK_TYPE,
        workspace=common_params.workspace,
    )

    rule = service.find_labeling_rule(
        dataset,
        rule_query=query,
    )
    return rule


@router.patch(
    f"{NEW_BASE_ENDPOINT}/labeling/rules/{{query}}",
    operation_id="update_rule",
    description="Update dataset labeling rule attributes",
    response_model=LabelingRule,
    response_model_exclude_none=True,
)
async def update_rule(
    name: str,
    query: str,
    update: UpdateLabelingRule,
    common_params: CommonTaskQueryParams = Depends(),
    service: TextClassificationService = Depends(
        TextClassificationService.get_instance
    ),
    datasets: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> LabelingRule:

    dataset = datasets.find_by_name(
        user=current_user,
        name=name,
        task=TASK_TYPE,
        workspace=common_params.workspace,
    )

    rule = service.update_labeling_rule(
        dataset,
        rule_query=query,
        labels=update.labels,
        description=update.description,
    )
    return rule
