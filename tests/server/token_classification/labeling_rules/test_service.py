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

import pytest

from argilla.server.errors import EntityNotFoundError
from argilla.server.services.tasks.token_classification.labeling_rules.service import (
    LabelingFunctionsService,
    LabelingRule,
    span_selector,
)
from argilla.server.services.tasks.token_classification.model import (
    EntitySpan,
    ServiceTokenClassificationAnnotation,
    ServiceTokenClassificationRecord,
)


@pytest.mark.parametrize(
    argnames=("text", "keywords", "expected"),
    argvalues=[
        (
            "The prior of Granada went to the park",
            ["Granada", "park"],
            ServiceTokenClassificationAnnotation(
                entities=[
                    EntitySpan(start=13, end=20, label="PETE"),
                    EntitySpan(start=33, end=37, label="PETE"),
                ]
            ),
        ),
        (
            "The prior of Granada went to the park",
            [],
            ServiceTokenClassificationAnnotation(entities=[]),
        ),
        (
            "The prior of Granada went to the park",
            None,
            ServiceTokenClassificationAnnotation(entities=[]),
        ),
        (
            "The prior of Granada went to the park of the hills",
            ["granada", "Granada", "of"],
            ServiceTokenClassificationAnnotation(
                entities=[
                    EntitySpan(start=10, end=12, label="PETE"),
                    EntitySpan(start=13, end=20, label="PETE"),
                    EntitySpan(start=38, end=40, label="PETE"),
                ],
            ),
        ),
    ],
)
def test_service(text, keywords, expected):
    service = LabelingFunctionsService()

    records = [
        ServiceTokenClassificationRecord(
            text=text,
            tokens=text.split(),
            search_keywords=keywords,
        )
    ]

    rule = LabelingRule(
        query="bad",
        label="PETE",
        selector="builtin::exact_match",
    )
    service.apply_rule(
        rule,
        records=records,
    )

    for record in records:
        assert rule.query in record.annotations
        assert record.annotations[rule.query] == expected
        for span in record.annotations[rule.query].entities:
            assert text[span.start : span.end] in keywords


def test_service_with_not_found_selector():
    service = LabelingFunctionsService()
    with pytest.raises(EntityNotFoundError, match="NOTFOUND"):
        service.apply_rule(
            LabelingRule(
                query="bd",
                label="lb",
                selector="NOTFOUND",
            ),
            records=[],
        )


def test_create_a_duplicated_selector():
    @span_selector(name="test")
    def test1(*args, **kwargs):
        return []

    with pytest.raises(
        ValueError,
        match="Span selector with name test already defined",
    ):

        @span_selector(name="test")
        def test2(*args, **kwargs):
            return []
