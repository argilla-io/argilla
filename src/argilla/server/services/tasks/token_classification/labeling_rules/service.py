#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import re
from typing import Callable, Dict, Iterable, List, Tuple, Union

from pydantic import BaseModel

from argilla.server.errors import EntityNotFoundError
from argilla.server.services.tasks.commons.mixins.labeling_rules import (
    LabelingRulesMixin,
)
from argilla.server.services.tasks.token_classification.model import ServiceLabelingRule
from argilla.server.services.tasks.token_classification.model import (
    ServiceTokenClassificationRecord,
)
from argilla.server.services.tasks.token_classification.model import (
    ServiceTokenClassificationRecord as Record,
)

SpanSelector = Callable[
    [Record],
    Union[List[Tuple[int, int]], Tuple[List[Tuple[int, int]], str]],
]


class EntitySpan(BaseModel):
    start: int
    end: int


class RuleRecordInfo(BaseModel):
    id: Union[str, int]
    entities: List[EntitySpan]


class LabelingFunctionsMixin:

    EXACT_MATCH_SELECTOR = "builtin::exact_match"

    __SELECTORS_MAP__: Dict[str, SpanSelector] = {}

    @classmethod
    def _span_selector(cls, name: str, selector: SpanSelector):
        if name in cls.__SELECTORS_MAP__:
            raise ValueError(
                f"Span selector with name {name} already defined. "
                "Please change the selector name"
            )

        cls.__SELECTORS_MAP__[name] = selector

    def apply_rule(
        self,
        rule: ServiceLabelingRule,
        records: Iterable[Record],
    ) -> List[RuleRecordInfo]:
        """Will update records annotation including a new agent corresponding to the rule id"""
        if not rule.span_selector:
            rule.span_selector = self._default_selector_id()
        span_selector_ = self._span_selector_by_rule(rule)
        result_records = []
        for record in records:
            spans = [
                EntitySpan(start=start, end=end)
                for start, end in span_selector_(record)
            ]
            result_records.append(RuleRecordInfo(id=record.id, entities=spans))
        return result_records

    def _span_selector_by_rule(self, rule: ServiceLabelingRule) -> SpanSelector:
        # The span selector can be defined in a decorated function or as a class implementation

        selector = self.__SELECTORS_MAP__.get(rule.span_selector)
        if not selector:
            raise EntityNotFoundError(
                name=rule.span_selector,
                type="SpanSelector",
            )
        return selector

    def _default_selector_id(self):
        return self.EXACT_MATCH_SELECTOR


def span_selector(name: str):
    "Decorate a function as an span selector"

    def inner(func: SpanSelector):
        LabelingFunctionsMixin._span_selector(name, func)
        return func

    return inner


class NERLabelingRulesMixin(
    LabelingRulesMixin[ServiceLabelingRule],
    LabelingFunctionsMixin,
):
    def _prepare_rule_for_save(self, rule: ServiceLabelingRule):
        if not rule.span_selector:
            rule.span_selector = LabelingFunctionsMixin.EXACT_MATCH_SELECTOR
        return rule


@span_selector(name=LabelingFunctionsMixin.EXACT_MATCH_SELECTOR)
def exact_match(record: ServiceTokenClassificationRecord) -> List[Tuple[int, int]]:
    """Given a text and a set of search keywords, this selector will match all keywords found in the text"""
    if not record.search_keywords:
        return []

    spans = []
    pattern = re.compile(rf"({'|'.join(record.search_keywords)})")
    for match in pattern.finditer(record.text):
        spans.append((match.start(), match.end()))
    return spans
