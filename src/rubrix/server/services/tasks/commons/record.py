from typing import Generic, TypeVar

from rubrix.server.daos.models.records import BaseAnnotation as _BaseAnnotation
from rubrix.server.daos.models.records import BaseRecordDB as _BaseRecordDB
from rubrix.server.daos.models.records import PredictionStatus as _PredictionStatus


class ServiceBaseAnnotation(_BaseAnnotation):
    pass


ServicePredictionStatus = _PredictionStatus
ServiceAnnotation = TypeVar("ServiceAnnotation", bound=ServiceBaseAnnotation)


class ServiceBaseRecord(_BaseRecordDB[ServiceAnnotation], Generic[ServiceAnnotation]):
    pass


ServiceRecord = TypeVar("ServiceRecord", bound=ServiceBaseRecord)
