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

import time
from typing import List

import pytest
from argilla_v1 import RGListenerContext, listener
from argilla_v1.client.api import delete, log
from argilla_v1.client.models import Record, TextClassificationRecord


def condition_check_params(search):
    if search:
        assert "param" in search.query_params and search.query_params["param"] == 100
    return True


@pytest.mark.parametrize(
    argnames=["dataset", "query", "metrics", "condition", "query_params"],
    argvalues=[
        ("dataset", None, ["F1"], None, None),
        ("dataset", "val", None, lambda s: True, None),
        ("dataset", None, ["F1"], lambda s, m: True, None),
        ("dataset", "val", None, None, None),
        ("dataset", None, ["F1"], lambda search, metrics: False, None),
        ("dataset", "val", None, lambda q: False, None),
        ("dataset", "val + {param}", None, condition_check_params, {"param": 100}),
    ],
)
def test_listener_with_parameters(mocked_client, dataset, query, metrics, condition, query_params):
    try:
        delete(dataset)
    except Exception:
        pass

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
        def action(self, records: List[Record], ctx: RGListenerContext):
            try:
                assert ctx.dataset == dataset
                if ctx.query_params:
                    assert ctx.query == query.format(**ctx.query_params)
                    if self.executed:
                        assert ctx.query_params != query_params
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
    log(TextClassificationRecord(text="This is a text"), name=dataset)

    with pytest.raises(ValueError):
        test.action.start()

    time.sleep(1.5)
    assert test.action.is_running()
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
