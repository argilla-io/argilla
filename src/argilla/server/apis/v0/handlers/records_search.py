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
from argilla.server.security import auth
from argilla.server.security.model import User
from argilla.server.services.datasets import DatasetsService

# TODO(@frascuchon): This will be merged with `records.py`
#  once the similarity search feature is merged into develop


def configure_router(router: APIRouter):
    QueryType = Union[
        TextClassificationQuery,
        TokenClassificationQuery,
        Text2TextQuery,
    ]

    class SearchRecordsRequest(BaseModel):
        query: Optional[QueryType]
        next_idx: Optional[str] = Field(description="Field to fetch data from a record id")
        fields: Optional[List[str]]
        sort_by: List[SortableField] = Field(
            default_factory=list,
            description="Set a sort config for records scan. "
            "The `next_id` field will be ignored if a sort configuration is found",
        )
        next_pagination_id: Optional[str] = Field(
            description="Field to paginate over scan results. Use value fetched from previous response"
        )

    class SearchRecordsResponse(BaseModel):
        records: List[dict]
        next_idx: Optional[str]
        next_pagination_id: Optional[str]

    @router.post("/{name}/records/:search", operation_id="scan_dataset_records", response_model=SearchRecordsResponse)
    async def scan_dataset_records(
        name: str,
        request: Optional[SearchRecordsRequest] = None,
        limit: int = Query(
            default=100,
            gte=0,
            le=500,
            description="Number of records to retrieve",
        ),
        request_deps: CommonTaskHandlerDependencies = Depends(),
        service: DatasetsService = Depends(DatasetsService.get_instance),
        engine: GenericElasticEngineBackend = Depends(GenericElasticEngineBackend.get_instance),
        current_user: User = Security(auth.get_user, scopes=[]),
    ):
        found = service.find_by_name(user=current_user, name=name, workspace=request_deps.workspace)
        request = request or SearchRecordsRequest()

        sort_info = PaginatedSortInfo(sort_by=request.sort_by or [SortableField(id="id")])
        if request.next_pagination_id:
            try:
                data = json.loads(request.next_pagination_id)
                sort_info = PaginatedSortInfo.parse_obj(data)
            except Exception as ex:
                pass
        elif request.next_idx and not request.sort_by:
            sort_info.next = [request.next_idx]

        docs = list(
            engine.scan_records(
                id=found.id,
                query=request.query,
                sort=sort_info,
                include_fields=request.fields,
                limit=limit,
            )
        )

        for doc in docs:
            sort_info.next = doc.pop("sort", None)

        return SearchRecordsResponse(
            next_idx=sort_info.next[0] if not request.sort_by else None,
            next_pagination_id=sort_info.json(),
            records=docs,
        )


router = APIRouter(
    tags=["datasets"],
    prefix="/datasets",
)
configure_router(router)
