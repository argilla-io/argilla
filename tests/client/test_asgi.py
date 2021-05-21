import rubrix
from rubrix import TextClassificationRecord, TokenClassificationRecord
from rubrix.client.asgi import RubrixLogHTTPMiddleware, token_classification_mapper
from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.testclient import TestClient


def test_rubrix_middleware_for_text_classification(monkeypatch):

    expected_endpoint = "/predict"
    expected_dataset_name = "mlmodel_v3_monitor_ds"

    app = Starlette()
    app.add_middleware(
        RubrixLogHTTPMiddleware,
        api_endpoint=expected_endpoint,
        dataset=expected_dataset_name,
    )

    @app.route(expected_endpoint, methods=["POST"])
    def mock_predict(request):
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

    mock.get("/another/predict/route")


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
    assert mock_log.was_called

    mock.get("/another/predict/route")
