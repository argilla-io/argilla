from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel


class _RuleUpdate(BaseModel):
    description: Optional[str] = Field(
        None, description="A brief description of the rule"
    )


class _RuleCreate(_RuleUpdate):
    query: str = Field(description="The es rule query")

    @validator("query")
    def strip_query(cls, query: str) -> str:
        """Remove blank spaces for query"""
        return query.strip()


class _Rule(_RuleCreate):
    author: str = Field(description="User who created the rule")
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow, description="Rule creation timestamp"
    )


class TextClassificationRuleUpdate(_RuleUpdate):
    labels: List[str] = Field(
        default_factory=list,
        description="For multi label problems, a list of labels. "
        "If no multi label, just one label will be accepted in list",
        min_items=1,
    )


class TextClassificationRuleCreate(_RuleCreate, TextClassificationRuleUpdate):
    pass


class TextClassificationRule(_Rule, TextClassificationRuleCreate):
    pass


class RuleMetrics(BaseModel):
    total_records: int
    annotated_records: int

    coverage: Optional[float] = None
    coverage_annotated: Optional[float] = None
    correct: Optional[float] = None
    incorrect: Optional[float] = None
    precision: Optional[float] = None


class DatasetRulesMetrics(BaseModel):
    total_records: int
    annotated_records: int

    coverage: Optional[float] = None
    coverage_annotated: Optional[float] = None


RuleType = TypeVar("RuleType", bound=_Rule)


class DatasetRules(GenericModel, Generic[RuleType]):

    total: int
    rules: List[RuleType]
