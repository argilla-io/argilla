from pydantic import BaseModel

from rubrix.client._apis.base import AbstractApi


class RubrixInfo(BaseModel):
    rubrix_version: str


class Status(AbstractApi):
    def get_info(self) -> RubrixInfo:
        response = self.__client__.get("/api/_info")
        return RubrixInfo.parse_obj(response)
