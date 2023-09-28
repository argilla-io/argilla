from typing import Generic, List, Literal, Optional, TypeVar, Union

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

from argilla.server.enums import MetadataPropertyType

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated


class TermsMetadataMetrics(BaseModel):
    class TermCount(BaseModel):
        term: str
        count: int

    type: Literal[MetadataPropertyType.terms] = Field(MetadataPropertyType.terms, const=True)
    total: int
    values: List[TermCount] = Field(default_factory=list)


NT = TypeVar("NT", int, float)


class NumericMetadataMetrics(GenericModel, Generic[NT]):
    min: Optional[NT]
    max: Optional[NT]


class IntegerMetadataMetrics(NumericMetadataMetrics[int]):
    type: Literal[MetadataPropertyType.integer] = Field(MetadataPropertyType.integer, const=True)


class FloatMetadataMetrics(NumericMetadataMetrics[float]):
    type: Literal[MetadataPropertyType.float] = Field(MetadataPropertyType.float, const=True)


MetadataMetrics = Annotated[
    Union[TermsMetadataMetrics, IntegerMetadataMetrics, FloatMetadataMetrics], Field(..., discriminator="type")
]
