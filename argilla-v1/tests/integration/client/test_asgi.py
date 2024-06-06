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

import argilla_v1
from argilla_server.models import User
from argilla_v1.monitoring.asgi import (
    ArgillaLogHTTPMiddleware,
    text_classification_mapper,
    token_classification_mapper,
)
from fastapi import FastAPI
from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.testclient import TestClient

from tests.integration.utils import delete_ignoring_errors


def test_argilla_middleware_for_text_classification(argilla_user: User):
    expected_endpoint = "/predict"
    expected_endpoint_get = "/predict_get"
    expected_dataset_name = "mlmodel_v3_monitor_ds"

    delete_ignoring_errors(expected_dataset_name)

    app = FastAPI()
    app.add_middleware(
        ArgillaLogHTTPMiddleware,
        api_endpoint=expected_endpoint,
        dataset=expected_dataset_name,
        records_mapper=text_classification_mapper,
        log_interval=0.1,
    )
    app.add_middleware(
        ArgillaLogHTTPMiddleware,
        api_endpoint=expected_endpoint_get,
        dataset=expected_dataset_name,
        records_mapper=text_classification_mapper,
        log_interval=0.1,
    )

    @app.route(expected_endpoint, methods=["POST", "PUT"])
    def mock_predict_post(data: Dict[str, Any]):
        return JSONResponse(content={"labels": ["A", "B"], "scores": [0.9, 0.1]})

    @app.route(expected_endpoint_get, methods=["GET"])
    def mock_predict_get(data: Dict[str, Any]):
        return JSONResponse(content={"labels": ["A", "B"], "scores": [0.9, 0.1]})

    @app.route("/another/predict/route")
    def another_mock(request):
        return PlainTextResponse("Hello")

    mock = TestClient(app)
    mock.post(
        expected_endpoint,
        json={"a": "The data input for A", "b": "The data input for B"},
    )

    time.sleep(0.5)
    df = argilla_v1.load(expected_dataset_name)
    df = df.to_pandas()
    assert len(df) == 1

    mock.put(
        expected_endpoint,
        json={"a": "The data input for A", "b": "The data input for B"},
    )
    time.sleep(0.5)
    df = argilla_v1.load(expected_dataset_name)
    df = df.to_pandas()
    assert len(df) == 2

    mock.get(
        expected_endpoint_get,
        params={"a": "The data input for A", "b": "The data input for B"},
    )
    time.sleep(0.5)
    df = argilla_v1.load(expected_dataset_name)
    df = df.to_pandas()
    assert len(df) == 3

    mock.get("/another/predict/route")

    time.sleep(0.5)
    df = argilla_v1.load(expected_dataset_name)
    df = df.to_pandas()
    assert len(df) == 3


def test_argilla_middleware_for_token_classification(argilla_user: User):
    expected_endpoint = "/predict"
    expected_endpoint_get = "/predict_get"
    expected_dataset_name = "mlmodel_v3_monitor_ds"
    delete_ignoring_errors(expected_dataset_name)

    app = Starlette()
    app.add_middleware(
        ArgillaLogHTTPMiddleware,
        api_endpoint=expected_endpoint,
        dataset=expected_dataset_name,
        records_mapper=token_classification_mapper,
        log_interval=0.1,
    )
    app.add_middleware(
        ArgillaLogHTTPMiddleware,
        api_endpoint=expected_endpoint_get,
        dataset=expected_dataset_name,
        records_mapper=token_classification_mapper,
        log_interval=0.1,
    )

    @app.route(expected_endpoint, methods=["POST", "PUT"])
    def mock_predict_post(request):
        return JSONResponse(
            content=[
                {"label": "fawn", "start": 0, "end": 3},
                {"label": "fobis", "start": 4, "end": 8},
            ]
        )

    @app.route(expected_endpoint_get, methods=["GET"])
    def mock_predict_get(request):
        return JSONResponse(
            content=[
                {"label": "fawn", "start": 0, "end": 3},
                {"label": "fobis", "start": 4, "end": 8},
            ]
        )

    @app.route("/another/predict/route")
    def another_mock(request):
        return PlainTextResponse("Hello")

    mock = TestClient(app)

    mock.post(
        expected_endpoint,
        json={"text": "The main text data"},
    )
    time.sleep(0.5)
    df = argilla_v1.load(expected_dataset_name)
    df = df.to_pandas()
    assert len(df) == 1

    mock.put(
        expected_endpoint,
        json={"text": "The main text data 3"},
    )
    time.sleep(0.5)
    df = argilla_v1.load(expected_dataset_name)
    df = df.to_pandas()
    assert len(df) == 2

    mock.get(
        expected_endpoint_get,
        params={"text": "The main text data 2"},
    )
    time.sleep(0.5)
    df = argilla_v1.load(expected_dataset_name)
    df = df.to_pandas()
    assert len(df) == 3

    mock.get("/another/predict/route")
    time.sleep(0.5)
    df = argilla_v1.load(expected_dataset_name)
    df = df.to_pandas()
    assert len(df) == 3
