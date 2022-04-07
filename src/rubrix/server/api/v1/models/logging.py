from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

from rubrix.server.tasks.commons import BaseRecord
from rubrix.server.tasks.text2text import CreationText2TextRecord
from rubrix.server.tasks.text_classification import CreationTextClassificationRecord
from rubrix.server.tasks.token_classification import CreationTokenClassificationRecord

Record = TypeVar("Record", bound=BaseRecord)


class AddRecordsRequest(GenericModel, Generic[Record]):
    records: List[Record]


class AddRecordsResponse(BaseModel):
    processed: int
    failed: Optional[int] = None


class TextClassificationRecord(CreationTextClassificationRecord):
    pass


class TokenClassificationRecord(CreationTokenClassificationRecord):
    pass


class Text2TextRecord(CreationText2TextRecord):  # TODO: User proper models
    pass
