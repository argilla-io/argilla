from typing import TypeVar

from rubrix.server.daos.models.records import BaseRecordDB as _BaseRecordDB


class ServiceBaseRecord(_BaseRecordDB):
    pass


ServiceRecord = TypeVar("ServiceRecord", bound=ServiceBaseRecord)
