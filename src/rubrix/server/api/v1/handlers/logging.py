from dataclasses import dataclass
from http import HTTPStatus
from typing import Union

from fastapi import APIRouter, Body, Depends, Path, Security

from rubrix.server.api.v1 import API_VERSION
from rubrix.server.api.v1.config.factory import __all__ as all_tasks
from rubrix.server.api.v1.models.commons.params import (
    DATASET_NAME_PATH_PARAM,
    WorkspaceParams,
)
from rubrix.server.api.v1.models.logging import AddRecordsRequest, LogRecordsResponse
from rubrix.server.commons.errors import EntityNotFoundError
from rubrix.server.datasets.service import DatasetsService
from rubrix.server.security import auth
from rubrix.server.security.model import User
from rubrix.server.tasks.search.model import BaseSearchQuery
from rubrix.server.tasks.search.service import SearchRecordsService

RECORD_ID_PATH_PARAM = Path(..., description="The record id param")


def configure_router() -> APIRouter:

    router = APIRouter(tags=[f"{API_VERSION} / Logging"])

    for cfg in all_tasks:
        base_endpoint = f"/{cfg.task}/{{name}}"
        service_class = cfg.service_class

        add_records_request_class = type(
            f"AddRecords_{cfg.task}", (AddRecordsRequest[cfg.record_class],), {}
        )

        @router.post(
            base_endpoint,
            name=f"{cfg.task}/log_records",
            operation_id=f"{cfg.task}/log_records",
            description=f"Log records into a {cfg.task} dataset",
            status_code=HTTPStatus.OK,
            response_model=LogRecordsResponse,
            response_model_exclude_none=True,
        )
        async def log_records(
            name: str = DATASET_NAME_PATH_PARAM,
            request: add_records_request_class = Body(
                ..., description="The collection of records to log"
            ),
            ws_params: WorkspaceParams = Depends(),
            datasets: DatasetsService = Depends(DatasetsService.get_instance),
            service: service_class = Depends(service_class.get_instance),
            user: User = Security(auth.get_user, scopes=["LogRecord"]),
        ) -> LogRecordsResponse:
            dataset = datasets.find_by_name(
                user=user,
                name=name,
                task=cfg.task,
                workspace=ws_params.workspace,
            )
            results = await service.add_records(
                dataset=dataset, records=request.records
            )
            return LogRecordsResponse(
                processed=results.processed, failed=results.failed
            )

        @router.put(
            path=f"{base_endpoint}/{{id}}",
            name=f"{cfg.task}/update_record",
            operation_id=f"{cfg.task}/update_record",
            description=f"Update a {cfg.task} record",
            status_code=HTTPStatus.OK,
            response_model=cfg.record_class,
            response_model_exclude_none=True,
        )
        async def update_record(
            name: str = DATASET_NAME_PATH_PARAM,
            id: Union[str, int] = RECORD_ID_PATH_PARAM,
            record: cfg.record_class = Body(..., description="The input record"),
            ws_params: WorkspaceParams = Depends(),
            datasets: DatasetsService = Depends(DatasetsService.get_instance),
            service: service_class = Depends(service_class.get_instance),
            search: SearchRecordsService = Depends(SearchRecordsService.get_instance),
            user: User = Security(auth.get_user, scopes=["LogRecord"]),
        ) -> cfg.record_class:

            dataset = datasets.find_by_name(
                user=user,
                name=name,
                task=cfg.task,
                workspace=ws_params.workspace,
            )
            found = search.search(
                dataset=dataset,
                record_type=cfg.record_class,
                query=BaseSearchQuery(ids=[id]),
            )
            if found.total <= 0:
                raise EntityNotFoundError(name=id, type=cfg.record_class)

            await service.add_records(dataset=dataset, records=[record])
            return record

        @router.patch(
            f"{base_endpoint}/{{id}}",
            name=f"{cfg.task}/partial_update_record",
            operation_id=f"{cfg.task}/partial_update_record",
            description=f"Partial update a {cfg.task} record",
            status_code=HTTPStatus.OK,
            response_model=cfg.record_class,
            response_model_exclude_none=True,
        )
        async def partial_update_record(
            name: str = DATASET_NAME_PATH_PARAM,
            id: Union[str, int] = RECORD_ID_PATH_PARAM,
            # TODO Partial record model
            request: cfg.record_class = Body(..., description="Record info to update"),
            ws_params: WorkspaceParams = Depends(),
            datasets: DatasetsService = Depends(DatasetsService.get_instance),
            search: SearchRecordsService = Depends(SearchRecordsService.get_instance),
            service: service_class = Depends(service_class.get_instance),
            user: User = Security(auth.get_user, scopes=["UpdateRecord"]),
        ) -> cfg.record_class:

            dataset = datasets.find_by_name(
                user=user,
                name=name,
                task=cfg.task,
                workspace=ws_params.workspace,
            )
            found = search.search(
                dataset=dataset,
                record_type=cfg.record_class,
                query=BaseSearchQuery(ids=[id]),
            )
            if found.total <= 0:
                raise EntityNotFoundError(name=id, type=cfg.record_class)

            found_record = found.records[0]
            record_for_update = found_record.copy(update=request)
            await service.add_records(dataset=dataset, records=[record_for_update])

            return record_for_update

    return router


__router__ = configure_router()
