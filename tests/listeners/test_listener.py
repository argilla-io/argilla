import time
from typing import List

import pytest

import rubrix as rb
from rubrix import RBListenerContext, listener
from rubrix.client.models import Record


@pytest.mark.parametrize(
    argnames=["dataset", "query", "metrics", "condition"],
    argvalues=[
        ("dataset", None, ["F1"], None),
        ("dataset", "val", None, lambda s: True),
        ("dataset", None, ["F1"], lambda s, m: True),
        ("dataset", "val", None, None),
        ("dataset", None, ["F1"], lambda search, metrics: False),
        ("dataset", "val", None, lambda q: False),
    ],
)
def test_listener_with_parameters(mocked_client, dataset, query, metrics, condition):
    rb.delete(dataset)

    class TestListener:
        executed = False
        error = None

        @listener(
            dataset=dataset,
            query=query,
            metrics=metrics,
            condition=condition,
            execution_interval_in_seconds=1,
        )
        def action(self, records: List[Record], ctx: RBListenerContext):
            try:
                self.executed = True

                assert ctx.dataset == dataset
                assert ctx.query == query
                if metrics:
                    for metric in metrics:
                        assert metric in ctx.metrics
            except Exception as error:
                self.error = error

    test = TestListener()
    test.action.start(test)

    time.sleep(1.5)
    rb.log(rb.TextClassificationRecord(text="This is a text"), name=dataset)

    with pytest.raises(ValueError):
        test.action.start()

    time.sleep(1.5)
    test.action.stop()

    with pytest.raises(ValueError):
        test.action.stop()

    if condition:
        res = condition(None, None) if metrics else condition(None)
        if not res:
            assert not test.executed, "Condition is False but action was executed"

    else:
        assert test.executed
        if test.error:
            raise test.error
