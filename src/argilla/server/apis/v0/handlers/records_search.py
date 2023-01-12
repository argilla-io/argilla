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

from typing import List, Optional, Union

from fastapi import APIRouter, Depends, Query, Security
from pydantic import BaseModel

from argilla.client.sdk.token_classification.models import TokenClassificationQuery
from argilla.server.apis.v0.models.commons.params import CommonTaskHandlerDependencies
from argilla.server.apis.v0.models.text2text import Text2TextQuery
from argilla.server.apis.v0.models.text_classification import TextClassificationQuery
from argilla.server.security import auth
from argilla.server.security.model import User
from argilla.server.services.datasets import DatasetsService
from argilla.server.services.search.service import SearchRecordsService

# TODO(@frascuchon): This will be merged with `records.py`
#  once the similarity search feature is merged into develop


def configure_router(router: APIRouter):
    QueryType = Union[
        TextClassificationQuery,
        TokenClassificationQuery,
        Text2TextQuery,
    ]

    class SearchRecordsRequest(BaseModel):
        query: Optional[QueryType] = None
        next_idx: Optional[str] = None
        fields: Optional[List[str]] = None

    class SearchRecordsResponse(BaseModel):
        next_idx: Optional[str]
        records: List[dict]

    @router.post(
        "/{name}/records/:search",
        operation_id="search_dataset_records",
        response_model=SearchRecordsResponse,
    )
    async def search_dataset_records(
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
        search: SearchRecordsService = Depends(SearchRecordsService.get_instance),
        current_user: User = Security(auth.get_user, scopes=[]),
    ):
        found = service.find_by_name(
            user=current_user,
            name=name,
            workspace=request_deps.workspace,
        )

        request = request or SearchRecordsRequest()

        docs = search.scan_records(
            dataset=found,
            query=request.query,
            id_from=request.next_idx,
            projection=request.fields,
            limit=limit,
        )
        docs = list(docs)
        last_doc = docs[-1] if docs else {}

        return SearchRecordsResponse(
            next_idx=last_doc.get("id"),
            records=docs,
        )


router = APIRouter(
    tags=["datasets"],
    prefix="/datasets",
)
configure_router(router)
