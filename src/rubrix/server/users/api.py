from fastapi import APIRouter, Security
from rubrix.server.security import auth

from .model import User

router = APIRouter(tags=["users"])


@router.get(
    "/me",
    response_model=User,
    response_model_exclude_none=True,
    operation_id="whoami",
)
async def whoami(current_user: User = Security(auth.get_user, scopes=[])):
    """
    User info endpoint

    Parameters
    ----------
    current_user:
        The current request user

    Returns
    -------
        The current user

    """
    return current_user
