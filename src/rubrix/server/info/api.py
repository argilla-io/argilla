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

from fastapi import APIRouter, Depends, Security
from rubrix.server.security import auth

from .model import ApiInfo, ApiStatus
from .service import ApiInfoService, create_info_service

router = APIRouter(tags=["status"])


@router.get(
    "/_status",
    operation_id="api_status",
    response_model=ApiStatus,
    dependencies=[Security(auth.get_user, scopes=[])],
)
def api_status(
    service: ApiInfoService = Depends(create_info_service),
) -> ApiStatus:
    """

    Parameters
    ----------
    service:
        The Api info service

    Returns
    -------

    The detailed api status

    """
    return service.api_status()


@router.get("/_info", operation_id="api_info", response_model=ApiInfo)
def api_info(
    service: ApiInfoService = Depends(create_info_service),
) -> ApiInfo:
    return ApiInfo.parse_obj(service.api_status())
