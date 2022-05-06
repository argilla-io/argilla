from typing import List, Optional, Union

from pydantic import BaseModel, Field, validator


class AbstractDatasetSettings(BaseModel):
    pass


class LabelsSchema(BaseModel):
    class Schema(BaseModel):
        id: str = Field(description="The label id")
        name: str = Field(description="The label name")
        description: Optional[str] = Field(None, description="The label description")

    labels: Union[List[str], List[Schema]] = Field(description="A set of labels")

    @validator("labels", pre=True)
    def normalize_labels(cls, labels):
        """
        Labels schema accept a list of strings. Those string will be converted
        into ``LabelsSchema.Schema`` objects
        """
        if not labels:
            return labels
        if isinstance(labels[0], str):
            return [LabelsSchema.Schema(id=label, name=label) for label in labels]
        return labels


class WithLabelsSchemaSettings(AbstractDatasetSettings):
    label_schema: Optional[LabelsSchema] = Field(
        None, description="The dataset labels schema"
    )


class TextClassificationSettings(WithLabelsSchemaSettings):
    pass


class TokenClassificationSettings(WithLabelsSchemaSettings):
    pass
