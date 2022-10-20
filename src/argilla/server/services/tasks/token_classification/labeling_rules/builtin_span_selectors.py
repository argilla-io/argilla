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
from typing import List, Tuple

from argilla.server.services.tasks.token_classification.labeling_rules.service import (
    span_selector,
)
from argilla.server.services.tasks.token_classification.model import (
    ServiceTokenClassificationRecord,
)


@span_selector(name="builtin::exact_match")
def exact_match(record: ServiceTokenClassificationRecord) -> List[Tuple[int, int]]:
    """Given a text and a set of search keywords, this selector will match all keywords found in the text"""
    if not record.search_keywords:
        return []

    spans = []
    pattern = re.compile(rf"({'|'.join(record.search_keywords)})")
    for match in pattern.finditer(record.text):
        spans.append((match.start(), match.end()))
    return spans
