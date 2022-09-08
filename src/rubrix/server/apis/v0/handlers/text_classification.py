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

from rubrix.server.apis.v0.handlers import text_classification_dataset_settings
from rubrix.server.apis.v0.models.commons.model import BulkResponse
from rubrix.server.apis.v0.models.commons.params import (
    CommonTaskHandlerDependencies,
    RequestPagination,
)
from rubrix.server.apis.v0.models.text_classification import (
    CreateLabelingRule,
    DatasetLabelingRulesMetricsSummary,
    LabelingRule,
    LabelingRuleMetricsSummary,
    TextClassificationBulkRequest,
    TextClassificationQuery,
    TextClassificationRecord,
    TextClassificationSearchAggregations,
    TextClassificationSearchRequest,
    TextClassificationSearchResults,
    UpdateLabelingRule,
)
from rubrix.server.apis.v0.models.token_classification import (
    TokenClassificationDataset,
    TokenClassificationQuery,
)
from rubrix.server.apis.v0.validators.text_classification import DatasetValidator
from rubrix.server.commons.config import TasksFactory
from rubrix.server.commons.models import TaskType
from rubrix.server.errors import EntityNotFoundError
from rubrix.server.helpers import takeuntil
from rubrix.server.responses import StreamingResponseWithErrorHandling
from rubrix.server.security import auth
from rubrix.server.security.model import User
from rubrix.server.services.datasets import DatasetsService
from rubrix.server.services.tasks.text_classification import TextClassificationService
from rubrix.server.services.tasks.text_classification.model import (
    ServiceLabelingRule,
    ServiceTextClassificationQuery,
    ServiceTextClassificationRecord,
)
from rubrix.server.services.tasks.token_classification.metrics import (
    TokenClassificationMetrics,
)
from rubrix.server.services.tasks.token_classification.model import (
    ServiceTokenClassificationRecord,
)

TASK_TYPE = TaskType.text_classification
BASE_ENDPOINT = "/{name}/" + TASK_TYPE
NEW_BASE_ENDPOINT = f"/{TASK_TYPE}/{{name}}"

TasksFactory.register_task(
    task_type=TaskType.token_classification,
    dataset_class=TokenClassificationDataset,
    query_request=TokenClassificationQuery,
    record_class=ServiceTokenClassificationRecord,
    metrics=TokenClassificationMetrics,
)


router = APIRouter(tags=[TASK_TYPE], prefix="/datasets")


@router.post(
    BASE_ENDPOINT + ":bulk",
    operation_id="bulk_records",
    response_model=BulkResponse,
    response_model_exclude_none=True,
)
async def bulk_records(
    name: str,
    bulk: TextClassificationBulkRequest,
    common_params: CommonTaskHandlerDependencies = Depends(),
    service: TextClassificationService = Depends(
        TextClassificationService.get_instance
    ),
    datasets: DatasetsService = Depends(DatasetsService.get_instance),
    validator: DatasetValidator = Depends(DatasetValidator.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> BulkResponse:

    task = TASK_TYPE
    owner = current_user.check_workspace(common_params.workspace)
    try:
        dataset = datasets.find_by_name(
            current_user,
            name=name,
            task=task,
            workspace=owner,
            as_dataset_class=TasksFactory.get_task_dataset(TASK_TYPE),
        )
        datasets.update(
            user=current_user,
            dataset=dataset,
            tags=bulk.tags,
            metadata=bulk.metadata,
        )
    except EntityNotFoundError:
        dataset_class = TasksFactory.get_task_dataset(task)
        dataset = dataset_class.parse_obj({**bulk.dict(), "name": name})
        dataset.owner = owner
        datasets.create_dataset(user=current_user, dataset=dataset)

    # TODO(@frascuchon): Validator should be applied in the service layer
    records = [ServiceTextClassificationRecord.parse_obj(r) for r in bulk.records]
    await validator.validate_dataset_records(
        user=current_user, dataset=dataset, records=records
    )

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
    BASE_ENDPOINT + ":search",
    response_model=TextClassificationSearchResults,
    response_model_exclude_none=True,
    operation_id="search_records",
)
def search_records(
    name: str,
    search: TextClassificationSearchRequest = None,
    common_params: CommonTaskHandlerDependencies = Depends(),
    include_metrics: bool = Query(
        False, description="If enabled, return related record metrics"
    ),
    pagination: RequestPagination = Depends(),
    service: TextClassificationService = Depends(
        TextClassificationService.get_instance
    ),
    datasets: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
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
        task=TASK_TYPE,
        workspace=common_params.workspace,
        as_dataset_class=TasksFactory.get_task_dataset(TASK_TYPE),
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
        aggregations=TextClassificationSearchAggregations.parse_obj(result.metrics)
        if result.metrics
        else None,
    )


def scan_data_response(
    data_stream: Iterable[TextClassificationRecord],
    chunk_size: int = 1000,
    limit: Optional[int] = None,
) -> StreamingResponseWithErrorHandling:
    """Generate an textual stream data response for a dataset scan"""

    async def stream_generator(stream):
        """Converts dataset scan into a text stream"""

        def grouper(n, iterable, fillvalue=None):
            args = [iter(iterable)] * n
            return itertools.zip_longest(fillvalue=fillvalue, *args)

        if limit:
            stream = takeuntil(stream, limit=limit)

        for batch in grouper(
            n=chunk_size,
            iterable=stream,
        ):
            filtered_records = filter(lambda r: r is not None, batch)
            yield "\n".join(
                map(
                    lambda r: r.json(by_alias=True, exclude_none=True), filtered_records
                )
            ) + "\n"

    return StreamingResponseWithErrorHandling(
        stream_generator(data_stream), media_type="application/json"
    )


@router.post(
    BASE_ENDPOINT + "/data",
    operation_id="stream_data",
)
async def stream_data(
    name: str,
    query: Optional[TextClassificationQuery] = None,
    common_params: CommonTaskHandlerDependencies = Depends(),
    id_from: Optional[str] = None,
    limit: Optional[int] = Query(None, description="Limit loaded records", gt=0),
    service: TextClassificationService = Depends(
        TextClassificationService.get_instance
    ),
    datasets: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> StreamingResponse:
    """
        Creates a data stream over dataset records

    Parameters
    ----------
    name
        The dataset name
    query:
        The stream data query
    common_params:
        Common query params
    limit:
        The load number of records limit. Optional
    service:
        The dataset records service
    datasets:
        The datasets service
    current_user:
        Request user

    id_from:
        Search after the given record ID

    """
    query = query or TextClassificationQuery()
    dataset = datasets.find_by_name(
        user=current_user,
        name=name,
        task=TASK_TYPE,
        workspace=common_params.workspace,
        as_dataset_class=TasksFactory.get_task_dataset(TASK_TYPE),
    )

    data_stream = map(
        TextClassificationRecord.parse_obj,
        service.read_dataset(
            dataset,
            query=ServiceTextClassificationQuery.parse_obj(query),
            id_from=id_from,
            limit=limit,
        ),
    )
    return scan_data_response(
        data_stream=data_stream,
        limit=limit,
    )


@router.get(
    f"{NEW_BASE_ENDPOINT}/labeling/rules",
    operation_id="list_labeling_rules",
    description="List all dataset labeling rules",
    response_model=List[LabelingRule],
    response_model_exclude_none=True,
)
async def list_labeling_rules(
    name: str,
    common_params: CommonTaskHandlerDependencies = Depends(),
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
        as_dataset_class=TasksFactory.get_task_dataset(TASK_TYPE),
    )

    return [
        LabelingRule.parse_obj(rule) for rule in service.get_labeling_rules(dataset)
    ]


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
    common_params: CommonTaskHandlerDependencies = Depends(),
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
        as_dataset_class=TasksFactory.get_task_dataset(TASK_TYPE),
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


@router.get(
    f"{NEW_BASE_ENDPOINT}/labeling/rules/{{query:path}}/metrics",
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
    common_params: CommonTaskHandlerDependencies = Depends(),
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
        as_dataset_class=TasksFactory.get_task_dataset(TASK_TYPE),
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
    common_params: CommonTaskHandlerDependencies = Depends(),
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
        as_dataset_class=TasksFactory.get_task_dataset(TASK_TYPE),
    )
    metrics = service.compute_overall_rules_metrics(dataset)
    return DatasetLabelingRulesMetricsSummary.parse_obj(metrics)


@router.delete(
    f"{NEW_BASE_ENDPOINT}/labeling/rules/{{query:path}}",
    operation_id="delete_labeling_rule",
    description="Deletes a labeling rule from dataset",
)
async def delete_labeling_rule(
    name: str,
    query: str,
    common_params: CommonTaskHandlerDependencies = Depends(),
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
        as_dataset_class=TasksFactory.get_task_dataset(TASK_TYPE),
    )

    service.delete_labeling_rule(dataset, rule_query=query)


@router.get(
    f"{NEW_BASE_ENDPOINT}/labeling/rules/{{query:path}}",
    operation_id="get_rule",
    description="Get the dataset labeling rule",
    response_model=LabelingRule,
    response_model_exclude_none=True,
)
async def get_rule(
    name: str,
    query: str,
    common_params: CommonTaskHandlerDependencies = Depends(),
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
        as_dataset_class=TasksFactory.get_task_dataset(TASK_TYPE),
    )
    rule = service.find_labeling_rule(
        dataset,
        rule_query=query,
    )
    return LabelingRule.parse_obj(rule)


@router.patch(
    f"{NEW_BASE_ENDPOINT}/labeling/rules/{{query:path}}",
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
        as_dataset_class=TasksFactory.get_task_dataset(TASK_TYPE),
    )

    rule = service.update_labeling_rule(
        dataset,
        rule_query=query,
        labels=update.labels,
        description=update.description,
    )
    return LabelingRule.parse_obj(rule)


text_classification_dataset_settings.configure_router(router)
