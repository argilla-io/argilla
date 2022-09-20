import time


def test_records_from_dataset(mocked_client):
    dataset = "test_records_from_dataset"
    import rubrix as rb

    rb.delete(dataset)
    rb.log(
        name=dataset,
        records=[
            rb.TextClassificationRecord(
                id=i, text="This is the text", metadata=dict(idx=i)
            )
            for i in range(0, 50)
        ],
    )

    matched, processed = rb.delete_records(name=dataset, ids=[10], discard_only=True)
    assert matched, processed == (1, 1)

    ds = rb.load(name=dataset)
    assert len(ds) == 50

    time.sleep(1)
    matched, processed = rb.delete_records(
        name=dataset, query="id:10", discard_only=False
    )
    assert matched, processed == (1, 1)

    time.sleep(1)
    ds = rb.load(name=dataset)
    assert len(ds) == 49
