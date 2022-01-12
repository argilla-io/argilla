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

from rubrix.server.commons.api import CommonTaskQueryParams
from rubrix.server.datasets.model import CreationDatasetRequest, Dataset
from rubrix.server.datasets.service import DatasetsService
from rubrix.server.security import auth
from rubrix.server.security.model import User
from rubrix.server.tasks.commons.api import BulkResponse, PaginationParams, TaskType
from rubrix.server.tasks.commons.helpers import takeuntil
from rubrix.server.tasks.text_classification.api.model import (
    CreateLabelingRule,
    DatasetLabelingRulesMetricsSummary,
    LabelingRule,
    LabelingRuleMetricsSummary,
    TextClassificationBulkData,
    TextClassificationQuery,
    TextClassificationRecord,
    TextClassificationSearchRequest,
    TextClassificationSearchResults,
    UpdateLabelingRule,
)
from rubrix.server.tasks.text_classification.service.service import (
    TextClassificationService,
)

TASK_TYPE = TaskType.text_classification
BASE_ENDPOINT = "/{name}/" + TASK_TYPE
NEW_BASE_ENDPOINT = f"/{TASK_TYPE}/{{name}}"

router = APIRouter(tags=[TASK_TYPE], prefix="/datasets")


@router.post(
    BASE_ENDPOINT + ":bulk",
    operation_id="bulk_records",
    response_model=BulkResponse,
    response_model_exclude_none=True,
)
def bulk_records(
    name: str,
    bulk: TextClassificationBulkData,
    common_params: CommonTaskQueryParams = Depends(),
    service: TextClassificationService = Depends(
        TextClassificationService.get_instance
    ),
    datasets: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> BulkResponse:
    """
    Includes a chunk of record data with provided dataset bulk information

    Parameters
    ----------
    name:
        The dataset name
    bulk:
        The bulk data
    common_params:
        Common query params
    service:
        the Service
    datasets:
        The dataset service
    current_user:
        Current request user

    Returns
    -------
        Bulk response data
    """

    task = TASK_TYPE
    dataset = datasets.upsert(
        CreationDatasetRequest(**{**bulk.dict(), "name": name}),
        task=task,
        user=current_user,
        workspace=common_params.workspace,
    )
    result = service.add_records(
        dataset=dataset,
        records=bulk.records,
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
    common_params: CommonTaskQueryParams = Depends(),
    include_metrics: bool = Query(
        False, description="If enabled, return related record metrics"
    ),
    pagination: PaginationParams = Depends(),
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
        name, task=TASK_TYPE, user=current_user, workspace=common_params.workspace
    )
    result = service.search(
        dataset=Dataset.parse_obj(dataset),
        query=query,
        sort_by=search.sort,
        record_from=pagination.from_,
        size=pagination.limit,
        exclude_metrics=not include_metrics,
    )

    return result


def scan_data_response(
    data_stream: Iterable[TextClassificationRecord],
    chunk_size: int = 1000,
    limit: Optional[int] = None,
) -> StreamingResponse:
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

    return StreamingResponse(
        stream_generator(data_stream), media_type="application/json"
    )


@router.post(
    BASE_ENDPOINT + "/data",
    operation_id="stream_data",
)
async def stream_data(
    name: str,
    query: Optional[TextClassificationQuery] = None,
    common_params: CommonTaskQueryParams = Depends(),
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

    """
    query = query or TextClassificationQuery()
    dataset = datasets.find_by_name(
        name, task=TASK_TYPE, user=current_user, workspace=common_params.workspace
    )
    data_stream = service.read_dataset(Dataset.parse_obj(dataset), query=query)

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
    common_params: CommonTaskQueryParams = Depends(),
    datasets: DatasetsService = Depends(DatasetsService.get_instance),
    service: TextClassificationService = Depends(
        TextClassificationService.get_instance
    ),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> List[LabelingRule]:

    dataset = datasets.find_by_name(
        name,
        task=TASK_TYPE,
        user=current_user,
        workspace=common_params.workspace,
    )

    return list(service.get_labeling_rules(Dataset.parse_obj(dataset)))


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
        name,
        task=TASK_TYPE,
        user=current_user,
        workspace=common_params.workspace,
    )

    rule = LabelingRule(
        **rule.dict(),
        author=current_user.username,
    )
    service.add_labeling_rule(
        Dataset.parse_obj(dataset),
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
    label: Optional[str] = Query(None, description="Label related to query rule"),
    common_params: CommonTaskQueryParams = Depends(),
    service: TextClassificationService = Depends(
        TextClassificationService.get_instance
    ),
    datasets: DatasetsService = Depends(DatasetsService.get_instance),
    current_user: User = Security(auth.get_user, scopes=[]),
) -> LabelingRuleMetricsSummary:
    dataset = datasets.find_by_name(
        name,
        task=TASK_TYPE,
        user=current_user,
        workspace=common_params.workspace,
    )

    return service.compute_rule_metrics(
        Dataset.parse_obj(dataset), rule_query=query, label=label
    )


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
        name,
        task=TASK_TYPE,
        user=current_user,
        workspace=common_params.workspace,
    )

    return service.compute_overall_rules_metrics(Dataset.parse_obj(dataset))


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
        name,
        task=TASK_TYPE,
        user=current_user,
        workspace=common_params.workspace,
    )

    service.delete_labeling_rule(Dataset.parse_obj(dataset), rule_query=query)


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
        name,
        task=TASK_TYPE,
        user=current_user,
        workspace=common_params.workspace,
    )

    rule = service.find_labeling_rule(
        Dataset.parse_obj(dataset),
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
        name,
        task=TASK_TYPE,
        user=current_user,
        workspace=common_params.workspace,
    )

    rule = service.update_labeling_rule(
        Dataset.parse_obj(dataset),
        rule_query=query,
        label=update.label,
        description=update.description,
    )
    return rule
