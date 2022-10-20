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

import dataclasses
from typing import Callable, Dict, Iterable, List, Tuple, Union

from argilla.server.errors import EntityNotFoundError
from argilla.server.services.tasks.token_classification.model import EntitySpan as Span
from argilla.server.services.tasks.token_classification.model import (
    ServiceTokenClassificationAnnotation as Annotation,
)
from argilla.server.services.tasks.token_classification.model import (
    ServiceTokenClassificationRecord as Record,
)


@dataclasses.dataclass
class LabelingRule:
    query: str
    label: str
    selector: str


SpanSelector = Callable[
    [Record],
    Union[List[Tuple[int, int]], Tuple[List[Tuple[int, int]], str]],
]


class LabelingFunctionsService:

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
        rule: LabelingRule,
        records: Iterable[Record],
    ) -> None:
        """Will update records annotation including a new agent corresponding to the rule id"""

        span_selector_ = self._span_selector_by_rule(rule)
        agent = rule.query
        for record in records:
            entities = [
                Span(start=start, end=end, label=rule.label)
                for start, end in span_selector_(record)
            ]
            weak_labels = Annotation(entities=entities)
            record.annotations[agent] = weak_labels

    def _span_selector_by_rule(self, rule: LabelingRule) -> SpanSelector:
        # The span selector can be defined in a decorated function or as a class implementation
        selector = self.__SELECTORS_MAP__.get(rule.selector)
        if not selector:
            raise EntityNotFoundError(
                name=rule.selector,
                type="SpanSelector",
            )
        return selector


def span_selector(name: str):
    "Decorate a function as an span selector"

    def inner(func: SpanSelector):
        LabelingFunctionsService._span_selector(name, func)
        return func

    return inner
