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

from argilla.client.api import active_api
from argilla.client.sdk.token_classification.models import TokenClassificationRecord


@pytest.mark.parametrize(
    argnames="fields",
    argvalues=(set(), {"text"}, {"tokens"}),
)
def test_scan_records(
    mocked_client,
    gutenberg_spacy_ner,
    fields,
):
    import pandas as pd

    import argilla as rg

    data = active_api().datasets.scan(
        name=gutenberg_spacy_ner,
        projection=fields,
    )

    df = pd.DataFrame(data=data).set_index("id", drop=True)
    ds = rg.load(gutenberg_spacy_ner)
    assert len(df) == len(ds)
    assert set([c for c in df.columns]) == fields
    print(df)


def test_scan_records_with_filter(
    mocked_client,
    gutenberg_spacy_ner,
):
    expected_id = "00c27206-da48-4fc3-aab7-4b730628f8ac"
    data = active_api().datasets.scan(
        name=gutenberg_spacy_ner,
        projection={"*"},
        query_text=f"id: {expected_id}",
    )
    data = list(data)
    assert len(data) == 1
    for d in data:
        assert expected_id == TokenClassificationRecord.parse_obj(d).id


def test_scan_records_without_results(
    mocked_client,
    gutenberg_spacy_ner,
):
    data = active_api().datasets.scan(
        name=gutenberg_spacy_ner,
        query_text="status: NO_DATA",
    )
    data = list(data)
    assert len(data) == 0
