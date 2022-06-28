import time
from typing import List

import pytest

import rubrix as rb
from rubrix import RBListenerContext, listener
from rubrix.client.models import Record


@pytest.mark.parametrize(
    argnames=["dataset", "query", "metrics", "condition", "query_params"],
    argvalues=[
        ("dataset", None, ["F1"], None, None),
        ("dataset", "val", None, lambda s: True, None),
        ("dataset", None, ["F1"], lambda s, m: True, None),
        ("dataset", "val", None, None, None),
        ("dataset", None, ["F1"], lambda search, metrics: False, None),
        ("dataset", "val", None, lambda q: False, None),
        ("dataset", "val + {param}", None, lambda q: True, {"param": 100}),
    ],
)
def test_listener_with_parameters(
    mocked_client, dataset, query, metrics, condition, query_params
):
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
            **(query_params or {}),
        )
        def action(self, records: List[Record], ctx: RBListenerContext):
            try:
                assert ctx.dataset == dataset
                if ctx.query_params:
                    assert ctx.query == query.format(**ctx.query_params)
                    if self.executed:
                        assert ctx.query_params != query_params
                    else:
                        assert ctx.query_params == query_params
                    ctx.query_params["params"] += 1
                else:
                    assert ctx.query == query

                self.executed = True

                if metrics:
                    for metric in metrics:
                        assert metric in ctx.metrics
            except Exception as error:
                self.error = error

    test = TestListener()
    test.action.start(test)

    time.sleep(1.5)
    assert test.action.is_running()
    rb.log(rb.TextClassificationRecord(text="This is a text"), name=dataset)

    with pytest.raises(ValueError):
        test.action.start()

    time.sleep(1.5)
    test.action.stop()
    assert not test.action.is_running()

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
