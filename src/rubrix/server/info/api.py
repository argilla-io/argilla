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
