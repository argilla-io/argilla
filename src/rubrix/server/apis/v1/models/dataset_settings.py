from typing import List, Optional, TypeVar

from pydantic import BaseModel, Field


class AbstractDatasetSettings(BaseModel):
    pass


DatasetSettings = TypeVar("DatasetSettings", bound=AbstractDatasetSettings)


class LabelsSchema(BaseModel):
    class Schema(BaseModel):
        id: str = Field(description="The label id")
        name: str = Field(description="The label name")
        description: Optional[str] = Field(None, description="The label description")

    labels: List[Schema] = Field(description="A set of labels")


class WithLabelsSchemaSettings(AbstractDatasetSettings):
    labels_schema: Optional[LabelsSchema] = Field(
        None, description="The dataset labels schema"
    )


class TextClassificationSettings(WithLabelsSchemaSettings):
    pass


class TokenClassificationSettings(WithLabelsSchemaSettings):
    pass
