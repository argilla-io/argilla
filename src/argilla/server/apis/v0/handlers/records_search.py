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
import json
from typing import List, Optional, Union

from fastapi import APIRouter, Depends, Query, Security
from pydantic import BaseModel, Field

from argilla.client.sdk.token_classification.models import TokenClassificationQuery
from argilla.server.apis.v0.models.commons.model import SortableField
from argilla.server.apis.v0.models.commons.params import CommonTaskHandlerDependencies
from argilla.server.apis.v0.models.text2text import Text2TextQuery
from argilla.server.apis.v0.models.text_classification import TextClassificationQuery
from argilla.server.daos.backend import GenericElasticEngineBackend
from argilla.server.daos.backend.generic_elastic import PaginatedSortInfo
from argilla.server.models import User
from argilla.server.security import auth
from argilla.server.services.datasets import DatasetsService

# TODO(@frascuchon): This will be merged with `records.py`
#  once the similarity search feature is merged into develop


def configure_router(router: APIRouter):
    QueryType = Union[
        TextClassificationQuery,
        TokenClassificationQuery,
        Text2TextQuery,
    ]

    class ScanDatasetRecordsRequest(BaseModel):
        query: Optional[QueryType]
        next_idx: Optional[str] = Field(description="Field to fetch data from a record id")
        fields: Optional[List[str]]
        sort_by: List[SortableField] = Field(
            default_factory=list,
            description="Set a sort config for records scan. "
            "The `next_id` field will be ignored if a sort configuration is found",
        )
        next_page_cfg: Optional[str] = Field(
            description="Field to paginate over scan results. Use value fetched from previous response"
        )

    class ScanDatasetRecordsResponse(BaseModel):
        records: List[dict]
        next_idx: Optional[str]
        next_page_cfg: Optional[str]

    @router.post(
        "/{name}/records/:search", operation_id="scan_dataset_records", response_model=ScanDatasetRecordsResponse
    )
    async def scan_dataset_records(
        name: str,
        request: Optional[ScanDatasetRecordsRequest] = None,
        limit: int = Query(
            default=100,
            gte=0,
            le=1000,
            description="Number of records to retrieve",
        ),
        request_deps: CommonTaskHandlerDependencies = Depends(),
        service: DatasetsService = Depends(DatasetsService.get_instance),
        engine: GenericElasticEngineBackend = Depends(GenericElasticEngineBackend.get_instance),
        current_user: User = Security(auth.get_current_user),
    ):
        found = service.find_by_name(user=current_user, name=name, workspace=request_deps.workspace)

        request = request or ScanDatasetRecordsRequest()
        paginated_sort = PaginatedSortInfo(sort_by=request.sort_by or [SortableField(id="id")])
        if request.next_page_cfg:
            try:
                data = json.loads(request.next_page_cfg)
                paginated_sort = PaginatedSortInfo.parse_obj(data)
            except Exception:
                pass
        elif request.next_idx and not request.sort_by:
            paginated_sort.next_search_params = [request.next_idx]

        docs = engine.scan_records(
            id=found.id, query=request.query, sort=paginated_sort, include_fields=request.fields, limit=limit
        )

        docs = list(docs)
        for doc in docs:
            # Removing sort config for each document and keep the last one, used for next page configuration
            paginated_sort.next_search_params = doc.pop("sort", None)

        next_idx = None
        if paginated_sort.next_search_params and not request.sort_by:
            next_idx = paginated_sort.next_search_params[0]

        return ScanDatasetRecordsResponse(next_idx=next_idx, next_page_cfg=paginated_sort.json(), records=docs)


router = APIRouter(tags=["datasets"], prefix="/datasets")
configure_router(router)
