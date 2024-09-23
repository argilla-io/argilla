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

from typing import Optional, List

from fastapi import Request
from starlette.routing import Route, Mount


def resolve_endpoint_path_for_request(request: Request) -> Optional[str]:
    """
    Resolves the configured route endpoint path for the incoming request

    Parameters:
        request (Request): The incoming request

    Returns:
        The route path for the incoming request. None if the route path cannot be resolved.
    """

    all_routes = request.scope.get("router").routes or []

    for route in all_routes:
        parent = None
        routes: List[Route] = [route]

        if isinstance(route, Mount):
            parent = route
            routes = [route for route in route.routes if isinstance(route, Route)]

        for route in routes:
            if route.endpoint == request.scope.get("endpoint"):
                route_path = route.path
                if parent:
                    route_path = f"{parent.path}{route_path}"

                return route_path
