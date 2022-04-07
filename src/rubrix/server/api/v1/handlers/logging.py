from dataclasses import dataclass

from fastapi import APIRouter, Body, Depends, Path, Security

from rubrix.server.api.v1 import API_VERSION
from rubrix.server.api.v1.config.factory import __all__ as all_tasks
from rubrix.server.api.v1.models.commons.params import NameEndpointHandlerParams
from rubrix.server.api.v1.models.logging import AddRecordsRequest, AddRecordsResponse
from rubrix.server.commons.errors import EntityNotFoundError
from rubrix.server.datasets.service import DatasetsService
from rubrix.server.security import auth
from rubrix.server.security.model import User
from rubrix.server.tasks.search.model import BaseSearchQuery
from rubrix.server.tasks.search.service import SearchRecordsService


@dataclass
class LoggingRecordHandlerParams(NameEndpointHandlerParams):
    id: str = Path(...)


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
            name=f"Add records to a {cfg.task} dataset",
            operation_id=f"{cfg.task}/add_records",
            response_model=AddRecordsResponse,
            response_model_exclude_none=True,
        )
        async def add_records(
            request: add_records_request_class,
            params: NameEndpointHandlerParams = Depends(),
            datasets: DatasetsService = Depends(DatasetsService.get_instance),
            service: service_class = Depends(service_class.get_instance),
            user: User = Security(auth.get_user, scopes=["read", "write"]),
        ) -> AddRecordsResponse:
            dataset = datasets.find_by_name(
                user=user,
                name=params.name,
                task=cfg.task,
                workspace=params.common.workspace,
            )
            results = await service.add_records(
                dataset=dataset, records=request.records
            )
            return AddRecordsResponse(
                processed=results.processed, failed=results.failed
            )

        @router.put(
            f"{base_endpoint }/{{id}}",
            name=f"Update a {cfg.task} record",
            response_model=cfg.record_class,
            response_model_exclude_none=True,
            operation_id=f"{cfg.task}/update_record",
        )
        async def update_record(
            record: cfg.record_class,
            params: LoggingRecordHandlerParams = Depends(),
            datasets: DatasetsService = Depends(DatasetsService.get_instance),
            service: service_class = Depends(service_class.get_instance),
            search: SearchRecordsService = Depends(SearchRecordsService.get_instance),
            user: User = Security(auth.get_user, scopes=["read", "write"]),
        ) -> cfg.record_class:

            dataset = datasets.find_by_name(
                user=user,
                name=params.name,
                task=cfg.task,
                workspace=params.common.workspace,
            )
            found = search.search(
                dataset=dataset,
                record_type=cfg.record_class,
                query=BaseSearchQuery(ids=[params.id]),
            )
            if found.total <= 0:
                raise EntityNotFoundError(name=params.id, type=cfg.record_class)
            await service.add_records(dataset=dataset, records=[record])
            return record

        @router.patch(
            f"{base_endpoint}/{{id}}",
            name=f"Partial update a {cfg.task} record",
            response_model=cfg.record_class,
            response_model_exclude_none=True,
            operation_id=f"{cfg.task}/partial_update_record",
        )
        async def partial_update_record(
            record: cfg.record_class = Body(...),  # TODO Partial record model
            params: LoggingRecordHandlerParams = Depends(),
            datasets: DatasetsService = Depends(DatasetsService.get_instance),
            search: SearchRecordsService = Depends(SearchRecordsService.get_instance),
            service: service_class = Depends(service_class.get_instance),
            user: User = Security(auth.get_user, scopes=["read", "write"]),
        ) -> cfg.record_class:
            dataset = datasets.find_by_name(
                user=user,
                name=params.name,
                task=cfg.task,
                workspace=params.common.workspace,
            )
            found = search.search(
                dataset=dataset,
                record_type=cfg.record_class,
                query=BaseSearchQuery(ids=[params.id]),
            )
            if found.total <= 0:
                raise EntityNotFoundError(name=params.id, type=cfg.record_class)

            found_record = found.records[0]
            record_for_update = found_record.copy(update=record)
            await service.add_records(dataset=dataset, records=[record_for_update])

            return record_for_update

    return router


__router__ = configure_router()
