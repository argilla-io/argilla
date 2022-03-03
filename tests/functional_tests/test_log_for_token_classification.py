import pytest

import rubrix
from rubrix import TokenClassificationRecord


def test_log_with_empty_text(mocked_client):
    dataset = "test_log_with_empty_text"
    text = " "

    rubrix.delete(dataset)
    with pytest.raises(Exception, match="No text or empty text provided"):
        rubrix.log(
            TokenClassificationRecord(id=0, text=text, tokens=["a", "b", "c"]),
            name=dataset,
        )


def test_log_with_empty_tokens_list(mocked_client):
    dataset = "test_log_with_empty_text"
    text = "The text"

    rubrix.delete(dataset)
    with pytest.raises(
        Exception,
        match="ensure this value has at least 1 items",
    ):
        rubrix.log(
            TokenClassificationRecord(id=0, text=text, tokens=[]),
            name=dataset,
        )


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
    rubrix.delete(dataset)
    rubrix.log(record, name=dataset)

    records = rubrix.load(dataset, as_pandas=False)
    assert len(records) == 1
    assert records[0].text == record.text
    assert records[0].tokens == record.tokens
    assert records[0].metrics == {
        "tokens": [
            {
                "idx": 0,
                "value": "'",
                "char_start": 0,
                "char_end": 0,
                "length": 1,
                "capitalness": "UPPER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 1,
                "value": "Secret",
                "char_start": 1,
                "char_end": 6,
                "length": 6,
                "capitalness": "FIRST",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 2,
                "value": "Story",
                "char_start": 8,
                "char_end": 12,
                "length": 5,
                "capitalness": "FIRST",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 3,
                "value": ":",
                "char_start": 14,
                "char_end": 14,
                "length": 1,
                "capitalness": "UPPER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 4,
                "value": "Última",
                "char_start": 16,
                "char_end": 21,
                "length": 6,
                "capitalness": "FIRST",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 5,
                "value": "hora",
                "char_start": 23,
                "char_end": 26,
                "length": 4,
                "capitalness": "LOWER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 6,
                "value": "'",
                "char_start": 27,
                "char_end": 27,
                "length": 1,
                "capitalness": "UPPER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 7,
                "value": "debuta",
                "char_start": 29,
                "char_end": 34,
                "length": 6,
                "capitalness": "LOWER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 8,
                "value": "con",
                "char_start": 36,
                "char_end": 38,
                "length": 3,
                "capitalness": "LOWER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 9,
                "value": "un",
                "char_start": 40,
                "char_end": 41,
                "length": 2,
                "capitalness": "LOWER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 10,
                "value": "pobre",
                "char_start": 43,
                "char_end": 47,
                "length": 5,
                "capitalness": "LOWER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 11,
                "value": "8.7%",
                "char_start": 49,
                "char_end": 52,
                "length": 4,
                "capitalness": "UPPER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 12,
                "value": "en",
                "char_start": 54,
                "char_end": 55,
                "length": 2,
                "capitalness": "LOWER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 13,
                "value": "el",
                "char_start": 57,
                "char_end": 58,
                "length": 2,
                "capitalness": "LOWER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 14,
                "value": "access",
                "char_start": 60,
                "char_end": 65,
                "length": 6,
                "capitalness": "LOWER",
                "score": None,
                "tag": "B-ENG",
                "custom": None,
            },
            {
                "idx": 15,
                "value": "de",
                "char_start": 67,
                "char_end": 68,
                "length": 2,
                "capitalness": "LOWER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 16,
                "value": "Telecinco",
                "char_start": 70,
                "char_end": 78,
                "length": 9,
                "capitalness": "FIRST",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 17,
                "value": "..",
                "char_start": 79,
                "char_end": 80,
                "length": 2,
                "capitalness": "UPPER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 18,
                "value": ".",
                "char_start": 82,
                "char_end": 82,
                "length": 1,
                "capitalness": "UPPER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 19,
                "value": "PROGRAMAS",
                "char_start": 84,
                "char_end": 92,
                "length": 9,
                "capitalness": "UPPER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 20,
                "value": "CON",
                "char_start": 94,
                "char_end": 96,
                "length": 3,
                "capitalness": "UPPER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 21,
                "value": "MEJOR",
                "char_start": 98,
                "char_end": 102,
                "length": 5,
                "capitalness": "UPPER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 22,
                "value": "CUOTA",
                "char_start": 104,
                "char_end": 108,
                "length": 5,
                "capitalness": "UPPER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 23,
                "value": "DEL",
                "char_start": 110,
                "char_end": 112,
                "length": 3,
                "capitalness": "UPPER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 24,
                "value": "LUNES",
                "char_start": 114,
                "char_end": 118,
                "length": 5,
                "capitalness": "UPPER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 25,
                "value": "(",
                "char_start": 120,
                "char_end": 120,
                "length": 1,
                "capitalness": "UPPER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 26,
                "value": "POR",
                "char_start": 121,
                "char_end": 123,
                "length": 3,
                "capitalness": "UPPER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 27,
                "value": "CADENAS",
                "char_start": 125,
                "char_end": 131,
                "length": 7,
                "capitalness": "UPPER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 28,
                "value": ")",
                "char_start": 132,
                "char_end": 132,
                "length": 1,
                "capitalness": "UPPER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 29,
                "value": ".",
                "char_start": 133,
                "char_end": 133,
                "length": 1,
                "capitalness": "UPPER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
            {
                "idx": 30,
                "value": ".",
                "char_start": 135,
                "char_end": 135,
                "length": 1,
                "capitalness": "UPPER",
                "score": None,
                "tag": "O",
                "custom": None,
            },
        ],
        "tokens_length": 31,
        "text_length": 137,
        "predicted": {
            "mentions": [
                {
                    "value": "access",
                    "label": "ENG",
                    "score": 1.0,
                    "capitalness": "LOWER",
                    "density": 0.03225806451612903,
                    "tokens_length": 1,
                    "chars_length": 6,
                }
            ]
        },
        "annotated": {"mentions": []},
    }


def test_search_keywords(mocked_client):
    dataset = "test_search_keywords"
    from datasets import load_dataset

    dataset_ds = load_dataset("rubrix/gutenberg_spacy-ner", split="train")
    dataset_rb = rubrix.read_datasets(dataset_ds, task="TokenClassification")

    rubrix.delete(dataset)
    rubrix.log(name=dataset, records=dataset_rb)

    df = rubrix.load(dataset, query="lis*")
    assert not df.empty
    assert "search_keywords" in df.columns
    top_keywords = set(
        [
            keyword
            for keywords in df.search_keywords.value_counts(sort=True, ascending=False)
            .index[:3]
            .tolist()
            for keyword in keywords
        ]
    )
    assert {"listened", "listen"} == top_keywords, top_keywords
