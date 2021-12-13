from typing import Optional

from pydantic import BaseModel

from rubrix.client.sdk.text_classification.models import (
    LabelingRule,
)


class Rule(BaseModel):
    query: str
    label: str
    name: Optional[str] = None

    @classmethod
    def from_sdk(cls, value: LabelingRule) -> "Rule":
        return cls(query=value.query, label=value.label, name=value.description)


class RuleMetrics(BaseModel):

    coverage: float
    precision: float
    correct: int
    incorrect: int
