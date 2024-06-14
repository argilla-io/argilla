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
import argilla_v1
import pytest
from argilla_v1 import TokenClassificationRecord
from argilla_v1.client.client import Argilla
from argilla_v1.client.sdk.commons.errors import NotFoundApiError
from argilla_v1.client.singleton import ArgillaSingleton
from argilla_v1.metrics import __all__ as ALL_METRICS
from argilla_v1.metrics import entity_consistency

from tests.integration.utils import delete_ignoring_errors


def test_log_with_empty_text(api: Argilla):
    dataset = "test_log_with_empty_text"
    text = " "

    delete_ignoring_errors(dataset)
    with pytest.raises(Exception, match="The provided `text` contains only whitespaces."):
        api.log(
            TokenClassificationRecord(id=0, text=text, tokens=["a", "b", "c"]),
            name=dataset,
        )


def test_log_with_empty_tokens_list(api: Argilla):
    dataset = "test_log_with_empty_text"
    text = "The text"

    delete_ignoring_errors(dataset)
    with pytest.raises(
        Exception,
        match="At least one token should be provided",
    ):
        api.log(
            TokenClassificationRecord(id=0, text=text, tokens=[]),
            name=dataset,
        )


def test_call_metrics_with_no_api_client_initialized(api: Argilla):
    for metric in ALL_METRICS:
        if metric == entity_consistency:
            continue

        ArgillaSingleton.clear()
        with pytest.raises(NotFoundApiError):
            metric("not_found")


def test_log_record_that_makes_me_cry(api: Argilla):
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
    delete_ignoring_errors(dataset)
    api.log(record, name=dataset)

    records = api.load(dataset)
    assert len(records) == 1
    assert records[0].text == record.text
    assert records[0].tokens == record.tokens
    assert records[0].metrics == {
        "tokens": [
            {"value": "'"},
            {"capitalness": "FIRST", "value": "Secret"},
            {"capitalness": "FIRST", "value": "Story"},
            {"value": ":"},
            {"capitalness": "FIRST", "value": "Última"},
            {"capitalness": "LOWER", "value": "hora"},
            {"value": "'"},
            {"capitalness": "LOWER", "value": "debuta"},
            {"capitalness": "LOWER", "value": "con"},
            {"capitalness": "LOWER", "value": "un"},
            {"capitalness": "LOWER", "value": "pobre"},
            {"value": "8.7%"},
            {"capitalness": "LOWER", "value": "en"},
            {"capitalness": "LOWER", "value": "el"},
            {"capitalness": "LOWER", "value": "access"},
            {"capitalness": "LOWER", "value": "de"},
            {"capitalness": "FIRST", "value": "Telecinco"},
            {"value": ".."},
            {"value": "."},
            {"capitalness": "UPPER", "value": "PROGRAMAS"},
            {"capitalness": "UPPER", "value": "CON"},
            {"capitalness": "UPPER", "value": "MEJOR"},
            {"capitalness": "UPPER", "value": "CUOTA"},
            {"capitalness": "UPPER", "value": "DEL"},
            {"capitalness": "UPPER", "value": "LUNES"},
            {"value": "("},
            {"capitalness": "UPPER", "value": "POR"},
            {"capitalness": "UPPER", "value": "CADENAS"},
            {"value": ")"},
            {"value": "."},
            {"value": "."},
        ],
        "text_length": 137,
        "predicted": {"mentions": [{"capitalness": "LOWER", "score": 0.0, "label": "ENG", "value": "access"}]},
        "annotated": {"mentions": []},
    }


def test_search_keywords(api: Argilla):
    dataset = "test_search_keywords"
    from datasets import load_dataset

    dataset_ds = load_dataset(
        "argilla/gutenberg_spacy-ner",
        split="train",
        # This revision does not includes the vectors info, so tests will pass
        revision="fff5f572e4cc3127f196f46ba3f9914c6fd0d763",
    )
    dataset_rb = argilla_v1.read_datasets(dataset_ds, task="TokenClassification")

    delete_ignoring_errors(dataset)
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


def test_log_data_with_vectors_and_update_ok(api: Argilla):
    dataset = "test_log_data_with_vectors_and_update_ok"
    text = "This is a text"
    delete_ignoring_errors(dataset)

    records = [
        argilla_v1.TokenClassificationRecord(
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


def test_log_data_with_vectors_and_partial_update_ok(api: Argilla):
    dataset = "test_log_data_and_partial_update_ok"
    text = "This is a text"
    expected_n_records = 10

    delete_ignoring_errors(dataset)

    # Logging records with vector info

    records = [
        argilla_v1.TokenClassificationRecord(id=i, text=text, tokens=text.split(), vectors={"test-vector": [i] * 5})
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


def test_logging_data_with_concurrency(api: Argilla):
    from datasets import load_dataset

    dataset = "test_logging_data_with_concurrency"
    dataset_ds = load_dataset("rubrix/gutenberg_spacy-ner", split="train")

    dataset_rb = argilla_v1.read_datasets(dataset_ds, task="TokenClassification")

    delete_ignoring_errors(dataset)
    api.log(name=dataset, records=dataset_rb, batch_size=int(len(dataset_ds) / 4), num_threads=4)

    ds = api.load(name=dataset)
    assert len(dataset_ds) == len(ds)
