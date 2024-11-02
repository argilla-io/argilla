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
from argilla_v1.client.api import load
from argilla_v1.client.sdk.token_classification.models import TokenClassificationRecord
from argilla_v1.client.singleton import active_api


@pytest.mark.parametrize(
    argnames="fields",
    argvalues=(set(), {"text"}, {"tokens"}),
)
def test_scan_records(gutenberg_spacy_ner, fields):
    import pandas as pd

    data = active_api().datasets.scan(
        name=gutenberg_spacy_ner,
        projection=fields,
    )

    df = pd.DataFrame(data=data).set_index("id", drop=True)
    ds = load(gutenberg_spacy_ner)
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


def test_scan_fail_negative_limit(
    mocked_client,
    gutenberg_spacy_ner,
):
    with pytest.raises(ValueError, match="limit.*negative"):
        data = active_api().datasets.scan(
            name=gutenberg_spacy_ner,
            limit=-20,
        )
        # Actually load the generator its data
        data = list(data)


@pytest.mark.parametrize(("limit"), [6, 23, 20])
@pytest.mark.parametrize(("load_method"), [lambda: active_api().datasets.scan, lambda: load])
def test_scan_efficient_limiting(
    monkeypatch: pytest.MonkeyPatch,
    limit,
    gutenberg_spacy_ner,
    load_method,
):
    method = load_method()
    batch_size = 10

    # Monkeypatch the .post() call to track with what URLs the server is called
    called_paths = []
    original_post = active_api().http_client.post

    def tracked_post(path, *args, **kwargs):
        called_paths.append(path)
        return original_post(path, *args, **kwargs)

    monkeypatch.setattr(active_api().http_client, "post", tracked_post)

    # Try to fetch `limit` samples from the 100
    data = method(name=gutenberg_spacy_ner, limit=limit, batch_size=10)
    data = list(data)

    # Ensure that `limit` samples were indeed fetched
    assert len(data) == limit
    # Ensure that the samples were fetched in the expected number of requests
    # Equivalent to math.upper(limit / batch_size):
    assert len(called_paths) == (limit - 1) // batch_size + 1

    if limit % batch_size == 0:
        # If limit is divisible by batch_size, then we expect all calls to have a limit of batch_size
        assert all(path.endswith(f"?limit={batch_size}") for path in called_paths)
    else:
        # Otherwise, expect all calls except for the last one to have a limit of batch_size
        # while the last one has limit limit % batch_size
        assert all(path.endswith(f"?limit={batch_size}") for path in called_paths[:-1])
        assert called_paths[-1].endswith(f"?limit={limit % batch_size}")
