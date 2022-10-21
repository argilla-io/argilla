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

from argilla.server.services.tasks.token_classification.labeling_rules import (
    exact_match,
)
from argilla.server.services.tasks.token_classification.model import (
    ServiceTokenClassificationRecord,
)


@pytest.mark.parametrize(
    argnames=("text", "keywords", "expected"),
    argvalues=[
        (
            "The prior of Granada went to the park",
            ["Granada", "park"],
            ["Granada", "park"],
        ),
        ("The prior of Granada went to the park", [], []),
        ("The prior of Granada went to the park", None, []),
        (
            "The prior of Granada went to the park of the hills",
            ["granada", "Granada", "of"],
            ["of", "Granada", "of"],
        ),
    ],
)
def test_exact_match(text, keywords, expected):
    record = ServiceTokenClassificationRecord(
        text=text,
        tokens=text.split(),
        search_keywords=keywords,
    )

    spans = exact_match(record)
    assert expected == [text[start:end] for (start, end) in spans]
