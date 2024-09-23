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

from fastapi import Request, APIRouter
from fastapi.routing import APIRoute
from starlette.routing import Mount

from argilla_server.utils._fastapi import resolve_endpoint_path_for_request


def mock_endpoint(*args, **kwargs):
    pass


class TestFastAPIUTils:
    def test_resolve_endpoint_path_for_request(self):
        request = Request(
            scope={
                "type": "http",
                "router": APIRouter(routes=[APIRoute(path="/api/endpoint", endpoint=mock_endpoint)]),
                "endpoint": mock_endpoint,
            }
        )

        endpoint_path = resolve_endpoint_path_for_request(request)
        assert endpoint_path == "/api/endpoint"

    def test_resolve_endpoint_path_for_request_with_mount(self):
        request = Request(
            scope={
                "type": "http",
                "router": APIRouter(
                    routes=[Mount(path="/api", routes=[APIRoute(path="/endpoint", endpoint=mock_endpoint)])],
                ),
                "endpoint": mock_endpoint,
            }
        )

        endpoint_path = resolve_endpoint_path_for_request(request)
        assert endpoint_path == "/api/endpoint"

    def test_resolve_endpoint_path_for_request_with_different_endpoint(self):
        request = Request(
            scope={
                "type": "http",
                "router": APIRouter(
                    routes=[APIRoute(path="/api/endpoint", endpoint=mock_endpoint)],
                ),
                "endpoint": lambda x: x,
            }
        )

        endpoint_path = resolve_endpoint_path_for_request(request)
        assert endpoint_path is None

    def test_resolve_endpoint_path_for_request_with_missing_endpoint(self):
        request = Request(
            scope={
                "type": "http",
                "router": APIRouter(
                    routes=[APIRoute(path="/api/endpoint", endpoint=mock_endpoint)],
                ),
            }
        )

        endpoint_path = resolve_endpoint_path_for_request(request)
        assert endpoint_path is None
