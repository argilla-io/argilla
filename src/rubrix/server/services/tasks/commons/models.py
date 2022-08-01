from typing import Generic, TypeVar

from pydantic import BaseModel

from rubrix.server.daos.models.records import BaseAnnotationDB, BaseRecordDB


class ServiceBaseAnnotation(BaseAnnotationDB):
    pass


class BulkResponse(BaseModel):
    dataset: str
    processed: int
    failed: int = 0


ServiceAnnotation = TypeVar("ServiceAnnotation", bound=ServiceBaseAnnotation)


class ServiceBaseRecord(BaseRecordDB[ServiceAnnotation], Generic[ServiceAnnotation]):
    pass


ServiceRecord = TypeVar("ServiceRecord", bound=ServiceBaseRecord)
