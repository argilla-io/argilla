from typing import Optional, Union

from fastapi import APIRouter, Depends, Query, Security
from pydantic import BaseModel

from rubrix.client.sdk.token_classification.models import TokenClassificationQuery
from rubrix.server.apis.v0.models.commons.params import CommonTaskHandlerDependencies
from rubrix.server.apis.v0.models.text2text import Text2TextQuery
from rubrix.server.apis.v0.models.text_classification import TextClassificationQuery
from rubrix.server.security import auth
from rubrix.server.security.model import User
from rubrix.server.services.datasets import DatasetsService
from rubrix.server.services.storage.service import RecordsStorageService


def configure_router(router: APIRouter):
    QueryType = Union[TextClassificationQuery, TokenClassificationQuery, Text2TextQuery]

    class DeleteRecordsResponse(BaseModel):
        matched: int
        processed: int

    @router.delete(
        "/{name}/data",
        operation_id="delete_dataset_records",
        response_model=DeleteRecordsResponse,
    )
    async def delete_dataset_records(
        name: str,
        query: Optional[QueryType] = None,
        mark_as_discarded=Query(
            default=False,
            title="If True, matched records won't be deleted."
            " Instead of that, the record status will be changed to `Discarded`",
        ),
        request_deps: CommonTaskHandlerDependencies = Depends(),
        service: DatasetsService = Depends(DatasetsService.get_instance),
        storage: RecordsStorageService = Depends(RecordsStorageService.get_instance),
        current_user: User = Security(auth.get_user, scopes=[]),
    ):
        found = service.find_by_name(
            user=current_user,
            name=name,
            workspace=request_deps.workspace,
        )

        result = await storage.delete_records(
            user=current_user,
            dataset=found,
            query=query,
            mark_as_discarded=mark_as_discarded,
        )

        return DeleteRecordsResponse(
            matched=result.processed,
            processed=result.deleted or result.discarded,
        )


router = APIRouter(tags=["datasets"], prefix="/datasets")
configure_router(router)
