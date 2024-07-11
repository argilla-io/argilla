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
from argilla_v1.client.feedback.integrations.huggingface.card import size_categories_parser


@pytest.mark.parametrize(
    "size,expected",
    [
        (1, "n<1K"),
        (999, "n<1K"),
        (1_000, "1K<n<10K"),
        (10_000_000_000_001, "n>1T"),
    ],
)
def test_size_categories_parser(size: int, expected: str) -> None:
    assert size_categories_parser(size) == expected
