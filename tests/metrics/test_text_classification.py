def test_metrics_for_text_classification(mocked_client):
    dataset = "test_metrics_for_text_classification"

    import rubrix as rb

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
                inputs={"text": "my first rubrix example"},
                prediction=[("ham", 0.8), ("spam", 0.2)],
                annotation=["ham"],
            ),
        ],
        name=dataset,
    )

    from rubrix.metrics.text_classification import f1, f1_multilabel

    results = f1(dataset)
    assert results
    assert results.data == {
        "f1_macro": 1.0,
        "f1_micro": 1.0,
        "ham_f1": 1.0,
        "ham_precision": 1.0,
        "ham_recall": 1.0,
        "precision_macro": 1.0,
        "precision_micro": 1.0,
        "recall_macro": 1.0,
        "recall_micro": 1.0,
        "spam_f1": 1.0,
        "spam_precision": 1.0,
        "spam_recall": 1.0,
    }
    results.visualize()

    results = f1_multilabel(dataset)
    assert results
    assert results.data == {
        "f1_macro": 1.0,
        "f1_micro": 1.0,
        "ham_f1": 1.0,
        "ham_precision": 1.0,
        "ham_recall": 1.0,
        "precision_macro": 1.0,
        "precision_micro": 1.0,
        "recall_macro": 1.0,
        "recall_micro": 1.0,
        "spam_f1": 1.0,
        "spam_precision": 1.0,
        "spam_recall": 1.0,
    }
    results.visualize()


def test_f1_without_results(mocked_client):
    dataset = "test_f1_without_results"
    import rubrix as rb

    rb.log(
        [
            rb.TextClassificationRecord(
                id=1,
                inputs={"text": "my first rubrix example"},
            ),
            rb.TextClassificationRecord(
                id=2,
                inputs={"text": "my first rubrix example"},
            ),
        ],
        name=dataset,
    )

    from rubrix.metrics.text_classification import f1

    results = f1(dataset)
    assert results
    assert results.data == {}
    results.visualize()
