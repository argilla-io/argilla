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

from fastapi import APIRouter, Depends, Request, Path
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.api.schemas.v1.oauth2 import Provider, Providers, Token
from argilla_server.contexts import accounts
from argilla_server.database import get_async_db
from argilla_server.errors.future import NotFoundError
from argilla_server.models import User, UserRole, Workspace, WorkspaceUser
from argilla_server.security.authentication.oauth2 import OAuth2ClientProvider
from argilla_server.security.authentication.userinfo import UserInfo
from argilla_server.security.settings import settings

router = APIRouter(prefix="/oauth2", tags=["Authentication"])


def get_provider_by_name_or_raise(provider: str = Path()) -> OAuth2ClientProvider:
    try:
        return settings.oauth.providers[provider]
    except KeyError:
        raise NotFoundError(message=f"OAuth Provider '{provider}' not found")


@router.get("/providers", response_model=Providers)
def list_providers() -> Providers:
    providers = [Provider(name=provider_name) for provider_name in settings.oauth.providers]
    return Providers(items=providers)


@router.get("/providers/{provider}/authentication")
async def get_authentication(
    request: Request,
    provider: OAuth2ClientProvider = Depends(get_provider_by_name_or_raise),
) -> RedirectResponse:
    return provider.authorization_redirect(request)


@router.get("/providers/{provider}/access-token", response_model=Token)
async def get_access_token(
    request: Request,
    provider: OAuth2ClientProvider = Depends(get_provider_by_name_or_raise),
    db: AsyncSession = Depends(get_async_db),
) -> Token:
    user_data = await provider.get_user_data(request)
    userinfo = UserInfo(user_data)

    if not userinfo.username:
        raise RuntimeError("OAuth error: Missing username")

    user_w_workspace = await accounts.get_user_by_username(db, username=userinfo.username)
    if user_w_workspace is None:
        exs_workspaces = await accounts.list_workspaces(db)
        exs_workspaces = [w.name for w in exs_workspaces]
        default_available_workspaces = [workspace.name for workspace in settings.oauth.allowed_workspaces]
        workspaces = userinfo.available_workspaces or default_available_workspaces
        # Check first if workspaces exist
        workspaces = [w for w in workspaces if w in exs_workspaces]

        user_w_workspace = await accounts.create_user_with_random_password(
            db,
            username=userinfo.username,
            first_name=userinfo.first_name,
            last_name=userinfo.last_name,
            role=userinfo.role,
            workspaces=workspaces,
        )
    else:
        # With existing user update the role if needed
        if user_w_workspace.role != userinfo.role:
            user_w_workspace = await user_w_workspace.update(db, role=userinfo.role)
        # With existing user update the workspaces if needed
        if user_w_workspace.role != UserRole.owner and set(user_w_workspace.workspaces) != set(
            userinfo.available_workspaces
        ):
            for workspace_name in userinfo.available_workspaces:
                workspace = await Workspace.get_by(db, name=workspace_name)
                if not workspace:
                    continue

                await WorkspaceUser.create(
                    db,
                    workspace_id=workspace.id,
                    user_id=user_w_workspace.id,
                    autocommit=False,
                )
            for workspace in user_w_workspace.workspaces:
                if workspace.name not in userinfo.available_workspaces:
                    ws_user = await WorkspaceUser.get_by(db, workspace_id=workspace.id, user_id=user_w_workspace.id)
                    await ws_user.delete(db, autocommit=False)
            await db.commit()

    return Token(access_token=accounts.generate_user_token(user_w_workspace))
