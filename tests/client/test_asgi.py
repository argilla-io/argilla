#  coding=utf-8
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
from typing import Any, Dict

import rubrix
from fastapi import FastAPI
from rubrix import TextClassificationRecord, TokenClassificationRecord
from rubrix.client.asgi import RubrixLogHTTPMiddleware, token_classification_mapper
from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.testclient import TestClient


def test_rubrix_middleware_for_text_classification(monkeypatch):

    expected_endpoint = "/predict"
    expected_dataset_name = "mlmodel_v3_monitor_ds"

    app = FastAPI()
    app.add_middleware(
        RubrixLogHTTPMiddleware,
        api_endpoint=expected_endpoint,
        dataset=expected_dataset_name,
    )

    @app.route(expected_endpoint, methods=["POST"])
    def mock_predict(data: Dict[str, Any]):
        return JSONResponse(
            content=[
                {"labels": ["A", "B"], "probabilities": [0.9, 0.1]},
                {"labels": ["A", "B"], "probabilities": [0.9, 0.1]},
            ]
        )

    @app.route("/another/predict/route")
    def another_mock(request):
        return PlainTextResponse("Hello")

    class MockLog:
        def __init__(self):
            self.was_called = False

        def __call__(self, records, name: str, **kwargs):
            self.was_called = True
            assert name == expected_dataset_name
            assert len(records) == 2
            assert isinstance(records[0], TextClassificationRecord)

    mock_log = MockLog()
    monkeypatch.setattr(rubrix, "log", mock_log)
    mock = TestClient(app)

    mock.post(
        expected_endpoint,
        json=[
            {"a": "The data input for A", "b": "The data input for B"},
            {"a": "The data input for A", "b": "The data input for B"},
        ],
    )

    assert mock_log.was_called
    time.sleep(0.200)
    mock_log.was_called = False
    mock.get("/another/predict/route")
    assert not mock_log.was_called


def test_rubrix_middleware_for_token_classification(monkeypatch):

    expected_endpoint = "/predict"
    expected_dataset_name = "mlmodel_v3_monitor_ds"

    app = Starlette()
    app.add_middleware(
        RubrixLogHTTPMiddleware,
        api_endpoint=expected_endpoint,
        dataset=expected_dataset_name,
        records_mapper=token_classification_mapper,
    )

    @app.route(expected_endpoint, methods=["POST"])
    def mock_predict(request):
        return JSONResponse(
            content=[
                [
                    {"label": "fawn", "start": 1, "end": 10},
                    {"label": "fobis", "start": 12, "end": 14},
                ],
                [],
            ]
        )

    class MockLog:
        def __init__(self):
            self.was_called = False

        def __call__(self, records, name: str, **kwargs):
            self.was_called = True
            assert name == expected_dataset_name
            assert len(records) == 2
            assert isinstance(records[0], TokenClassificationRecord)

    mock_log = MockLog()
    monkeypatch.setattr(rubrix, "log", mock_log)
    mock = TestClient(app)

    mock.post(
        expected_endpoint,
        json=[{"text": "The main text data"}, {"text": "The main text data"}],
    )
    time.sleep(0.2)
    assert mock_log.was_called

    mock_log.was_called = False
    mock.get("/another/predict/route")

    time.sleep(0.2)
    assert not mock_log.was_called
