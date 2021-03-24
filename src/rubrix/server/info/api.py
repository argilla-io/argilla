from fastapi import APIRouter, Depends
from rubrix.server.security.api import get_current_active_user
from rubrix.server.users.model import User

from .model import ApiInfo, ApiStatus
from .service import ApiInfoService, create_info_service

router = APIRouter(tags=["status"])


@router.get("/_status", operation_id="api_status", response_model=ApiStatus)
def api_status(
    current_user: User = Depends(get_current_active_user),
    service: ApiInfoService = Depends(create_info_service),
) -> ApiStatus:
    """

    Parameters
    ----------
    current_user:
        Connected user (since protected endpoint)
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
