import httpx


def test_status_distribution(mocked_client):
    dataset = "test_status_distribution"

    import rubrix as rb

    rb.delete(dataset)

    rb.log(
        [
            rb.TextClassificationRecord(
                id=1,
                inputs={"text": "my first rubrix example"},
                prediction=[("spam", 0.8), ("ham", 0.2)],
                annotation=["spam"],
            ),
            rb.TextClassificationRecord(
                id=2,
                inputs={"text": "my second rubrix example"},
                prediction=[("ham", 0.8), ("spam", 0.2)],
                annotation=["ham"],
                status="Default",
            ),
        ],
        name=dataset,
    )

    from rubrix.metrics.commons import records_status

    results = records_status(dataset)
    assert results
    assert results.data == {"Default": 1, "Validated": 1}
    results.visualize()


def test_text_length(mocked_client):
    dataset = "test_text_length"

    import rubrix as rb

    rb.delete(dataset)

    rb.log(
        [
            rb.TextClassificationRecord(
                id=1,
                inputs={"text": "my first rubrix example"},
                prediction=[("spam", 0.8), ("ham", 0.2)],
                annotation=["spam"],
            ),
            rb.TextClassificationRecord(
                id=2,
                inputs={"text": "my second rubrix example"},
                prediction=[("ham", 0.8), ("spam", 0.2)],
                annotation=["ham"],
                status="Default",
            ),
            rb.TextClassificationRecord(
                id=3,
                inputs={"text": "simple text"},
                prediction=[("ham", 0.8), ("spam", 0.2)],
                annotation=["ham"],
            ),
        ],
        name=dataset,
    )

    from rubrix.metrics.commons import text_length

    results = text_length(dataset)
    assert results
    assert results.data == {
        "11.0": 1,
        "12.0": 0,
        "13.0": 0,
        "14.0": 0,
        "15.0": 0,
        "16.0": 0,
        "17.0": 0,
        "18.0": 0,
        "19.0": 0,
        "20.0": 0,
        "21.0": 0,
        "22.0": 0,
        "23.0": 1,
        "24.0": 1,
    }
    results.visualize()
