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

import argilla
import pytest
from argilla import TokenClassificationRecord
from argilla.client import api
from argilla.client.sdk.commons.errors import NotFoundApiError
from argilla.metrics import __all__ as ALL_METRICS
from argilla.metrics import entity_consistency

from tests.client.conftest import SUPPORTED_VECTOR_SEARCH
from tests.helpers import SecuredClient


def test_log_with_empty_text(mocked_client):
    dataset = "test_log_with_empty_text"
    text = " "

    argilla.delete(dataset)
    with pytest.raises(Exception, match="The provided `text` contains only whitespaces."):
        argilla.log(
            TokenClassificationRecord(id=0, text=text, tokens=["a", "b", "c"]),
            name=dataset,
        )


def test_log_with_empty_tokens_list(mocked_client):
    dataset = "test_log_with_empty_text"
    text = "The text"

    argilla.delete(dataset)
    with pytest.raises(
        Exception,
        match="At least one token should be provided",
    ):
        argilla.log(
            TokenClassificationRecord(id=0, text=text, tokens=[]),
            name=dataset,
        )


def test_call_metrics_with_no_api_client_initialized(mocked_client):
    for metric in ALL_METRICS:
        if metric == entity_consistency:
            continue

        api.ArgillaSingleton.clear()
        with pytest.raises(NotFoundApiError):
            metric("not_found")


def test_log_record_that_makes_me_cry(mocked_client):
    dataset = "test_log_record_that_makes_me_cry"
    record = TokenClassificationRecord(
        text="'Secret Story : Última hora' debuta con un pobre 8.7% en el access de Telecinco.. . "
        "PROGRAMAS CON MEJOR CUOTA DEL LUNES (POR CADENAS). . ",
        tokens=[
            "'",
            "Secret",
            "Story",
            ":",
            "Última",
            "hora",
            "'",
            "debuta",
            "con",
            "un",
            "pobre",
            "8.7%",
            "en",
            "el",
            "access",
            "de",
            "Telecinco",
            "..",
            ".",
            "PROGRAMAS",
            "CON",
            "MEJOR",
            "CUOTA",
            "DEL",
            "LUNES",
            "(",
            "POR",
            "CADENAS",
            ")",
            ".",
            ".",
        ],
        prediction=[("ENG", 60, 66)],
        annotation=None,
        prediction_agent=None,
        annotation_agent=None,
        id=None,
        metadata={"section": "television", "newspaper": "eldiario"},
        status="Default",
        event_timestamp=None,
    )
    argilla.delete(dataset)
    argilla.log(record, name=dataset)

    records = argilla.load(dataset)
    assert len(records) == 1
    assert records[0].text == record.text
    assert records[0].tokens == record.tokens
    assert records[0].metrics == {
        "annotated": {"mentions": [], "tags": []},
        "predicted": {
            "mentions": [
                {
                    "capitalness": "LOWER",
                    "chars_length": 6,
                    "density": 0.03225806451612903,
                    "label": "ENG",
                    "score": 0.0,
                    "tokens_length": 1,
                    "value": "access",
                }
            ],
            "tags": [
                {"tag": "O", "value": "'"},
                {"tag": "O", "value": "Secret"},
                {"tag": "O", "value": "Story"},
                {"tag": "O", "value": ":"},
                {"tag": "O", "value": "Última"},
                {"tag": "O", "value": "hora"},
                {"tag": "O", "value": "'"},
                {"tag": "O", "value": "debuta"},
                {"tag": "O", "value": "con"},
                {"tag": "O", "value": "un"},
                {"tag": "O", "value": "pobre"},
                {"tag": "O", "value": "8.7%"},
                {"tag": "O", "value": "en"},
                {"tag": "O", "value": "el"},
                {"tag": "B-ENG", "value": "access"},
                {"tag": "O", "value": "de"},
                {"tag": "O", "value": "Telecinco"},
                {"tag": "O", "value": ".."},
                {"tag": "O", "value": "."},
                {"tag": "O", "value": "PROGRAMAS"},
                {"tag": "O", "value": "CON"},
                {"tag": "O", "value": "MEJOR"},
                {"tag": "O", "value": "CUOTA"},
                {"tag": "O", "value": "DEL"},
                {"tag": "O", "value": "LUNES"},
                {"tag": "O", "value": "("},
                {"tag": "O", "value": "POR"},
                {"tag": "O", "value": "CADENAS"},
                {"tag": "O", "value": ")"},
                {"tag": "O", "value": "."},
                {"tag": "O", "value": "."},
            ],
        },
        "text_length": 137,
        "tokens": [
            {
                "char_end": 0,
                "char_start": 0,
                "idx": 0,
                "length": 1,
                "tag": "O",
                "value": "'",
            },
            {
                "capitalness": "FIRST",
                "char_end": 6,
                "char_start": 1,
                "idx": 1,
                "length": 6,
                "tag": "O",
                "value": "Secret",
            },
            {
                "capitalness": "FIRST",
                "char_end": 12,
                "char_start": 8,
                "idx": 2,
                "length": 5,
                "tag": "O",
                "value": "Story",
            },
            {
                "char_end": 14,
                "char_start": 14,
                "idx": 3,
                "length": 1,
                "tag": "O",
                "value": ":",
            },
            {
                "capitalness": "FIRST",
                "char_end": 21,
                "char_start": 16,
                "idx": 4,
                "length": 6,
                "tag": "O",
                "value": "Última",
            },
            {
                "capitalness": "LOWER",
                "char_end": 26,
                "char_start": 23,
                "idx": 5,
                "length": 4,
                "tag": "O",
                "value": "hora",
            },
            {
                "char_end": 27,
                "char_start": 27,
                "idx": 6,
                "length": 1,
                "tag": "O",
                "value": "'",
            },
            {
                "capitalness": "LOWER",
                "char_end": 34,
                "char_start": 29,
                "idx": 7,
                "length": 6,
                "tag": "O",
                "value": "debuta",
            },
            {
                "capitalness": "LOWER",
                "char_end": 38,
                "char_start": 36,
                "idx": 8,
                "length": 3,
                "tag": "O",
                "value": "con",
            },
            {
                "capitalness": "LOWER",
                "char_end": 41,
                "char_start": 40,
                "idx": 9,
                "length": 2,
                "tag": "O",
                "value": "un",
            },
            {
                "capitalness": "LOWER",
                "char_end": 47,
                "char_start": 43,
                "idx": 10,
                "length": 5,
                "tag": "O",
                "value": "pobre",
            },
            {
                "char_end": 52,
                "char_start": 49,
                "idx": 11,
                "length": 4,
                "tag": "O",
                "value": "8.7%",
            },
            {
                "capitalness": "LOWER",
                "char_end": 55,
                "char_start": 54,
                "idx": 12,
                "length": 2,
                "tag": "O",
                "value": "en",
            },
            {
                "capitalness": "LOWER",
                "char_end": 58,
                "char_start": 57,
                "idx": 13,
                "length": 2,
                "tag": "O",
                "value": "el",
            },
            {
                "capitalness": "LOWER",
                "char_end": 65,
                "char_start": 60,
                "idx": 14,
                "length": 6,
                "tag": "B-ENG",
                "value": "access",
            },
            {
                "capitalness": "LOWER",
                "char_end": 68,
                "char_start": 67,
                "idx": 15,
                "length": 2,
                "tag": "O",
                "value": "de",
            },
            {
                "capitalness": "FIRST",
                "char_end": 78,
                "char_start": 70,
                "idx": 16,
                "length": 9,
                "tag": "O",
                "value": "Telecinco",
            },
            {
                "char_end": 80,
                "char_start": 79,
                "idx": 17,
                "length": 2,
                "tag": "O",
                "value": "..",
            },
            {
                "char_end": 82,
                "char_start": 82,
                "idx": 18,
                "length": 1,
                "tag": "O",
                "value": ".",
            },
            {
                "capitalness": "UPPER",
                "char_end": 92,
                "char_start": 84,
                "idx": 19,
                "length": 9,
                "tag": "O",
                "value": "PROGRAMAS",
            },
            {
                "capitalness": "UPPER",
                "char_end": 96,
                "char_start": 94,
                "idx": 20,
                "length": 3,
                "tag": "O",
                "value": "CON",
            },
            {
                "capitalness": "UPPER",
                "char_end": 102,
                "char_start": 98,
                "idx": 21,
                "length": 5,
                "tag": "O",
                "value": "MEJOR",
            },
            {
                "capitalness": "UPPER",
                "char_end": 108,
                "char_start": 104,
                "idx": 22,
                "length": 5,
                "tag": "O",
                "value": "CUOTA",
            },
            {
                "capitalness": "UPPER",
                "char_end": 112,
                "char_start": 110,
                "idx": 23,
                "length": 3,
                "tag": "O",
                "value": "DEL",
            },
            {
                "capitalness": "UPPER",
                "char_end": 118,
                "char_start": 114,
                "idx": 24,
                "length": 5,
                "tag": "O",
                "value": "LUNES",
            },
            {
                "char_end": 120,
                "char_start": 120,
                "idx": 25,
                "length": 1,
                "tag": "O",
                "value": "(",
            },
            {
                "capitalness": "UPPER",
                "char_end": 123,
                "char_start": 121,
                "idx": 26,
                "length": 3,
                "tag": "O",
                "value": "POR",
            },
            {
                "capitalness": "UPPER",
                "char_end": 131,
                "char_start": 125,
                "idx": 27,
                "length": 7,
                "tag": "O",
                "value": "CADENAS",
            },
            {
                "char_end": 132,
                "char_start": 132,
                "idx": 28,
                "length": 1,
                "tag": "O",
                "value": ")",
            },
            {
                "char_end": 133,
                "char_start": 133,
                "idx": 29,
                "length": 1,
                "tag": "O",
                "value": ".",
            },
            {
                "char_end": 135,
                "char_start": 135,
                "idx": 30,
                "length": 1,
                "tag": "O",
                "value": ".",
            },
        ],
        "tokens_length": 31,
    }


def test_search_keywords(mocked_client, api):
    dataset = "test_search_keywords"
    from datasets import load_dataset

    # TODO(@frascuchon): Move dataset to new organization
    dataset_ds = load_dataset("rubrix/gutenberg_spacy-ner", split="train")
    dataset_rb = argilla.read_datasets(dataset_ds, task="TokenClassification")

    api.delete(dataset)
    api.log(name=dataset, records=dataset_rb)

    df = api.load(dataset, query="lis*")
    df = df.to_pandas()
    assert not df.empty
    assert "search_keywords" in df.columns
    top_keywords = set(
        [
            keyword
            for keywords in df.search_keywords.value_counts(sort=True, ascending=False).index[:3].tolist()
            for keyword in keywords
        ]
    )
    assert {"listened", "listen"} == top_keywords, top_keywords


@pytest.mark.skipif(
    condition=not SUPPORTED_VECTOR_SEARCH,
    reason="Vector search not supported",
)
def test_log_data_with_vectors_and_update_ok(mocked_client: SecuredClient, api):
    dataset = "test_log_data_with_vectors_and_update_ok"
    text = "This is a text"
    api.delete(dataset)

    records = [
        argilla.TokenClassificationRecord(
            id=i,
            text=text,
            tokens=text.split(),
            vectors={"test-vector": [i] * 5},
        )
        for i in range(1, 10)
    ]

    api.log(
        records=records,
        name=dataset,
    )
    ds = api.load(
        dataset,
        vector=(
            "test-vector",
            [3, 3, 2, 3, 3],  # the first expected records should be the id=3
        ),
        limit=5,
    )

    assert len(ds) == 5
    assert ds[0].id == 3


@pytest.mark.skipif(
    condition=not SUPPORTED_VECTOR_SEARCH,
    reason="Vector search not supported",
)
def test_log_data_with_vectors_and_partial_update_ok(mocked_client: SecuredClient, api):
    dataset = "test_log_data_and_partial_update_ok"
    text = "This is a text"
    expected_n_records = 10

    api.delete(dataset)

    # Logging records with vector info

    records = [
        argilla.TokenClassificationRecord(id=i, text=text, tokens=text.split(), vectors={"test-vector": [i] * 5})
        for i in range(0, expected_n_records)
    ]
    api.log(records=records, name=dataset)

    ds = api.load(dataset)
    assert len(ds) == expected_n_records
    assert all(map(lambda r: "test-vector" in r.vectors, ds))

    # Fetch minimal record info and add a metadata field
    records_for_update = [
        TokenClassificationRecord.parse_obj({"metadata": {"a": "value"}, **data})
        for data in api.datasets.scan(name=dataset, projection={"text", "tokens"})
    ]
    api.log(name=dataset, records=records_for_update)

    ds = api.load(dataset)
    assert len(ds) == expected_n_records
    assert all(map(lambda r: r.annotation_agent is None, ds))
    assert all(map(lambda r: "test-vector" in r.vectors, ds))
    assert all(map(lambda r: r.metadata == {"a": "value"}, ds))

    # Remove the metadata info and add some mock annotations
    for record in records_for_update:
        record.metadata = None
        record.annotation = []
        record.annotation_agent = "mock_test"
    api.log(name=dataset, records=records_for_update)

    ds = api.load(dataset)
    assert len(ds) == expected_n_records
    assert all(map(lambda r: r.annotation_agent == "mock_test", ds))
    assert all(map(lambda r: "test-vector" in r.vectors, ds))
    assert all(map(lambda r: r.metadata == {"a": "value"}, ds))
