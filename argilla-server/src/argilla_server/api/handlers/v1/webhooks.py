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

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Security, status

from argilla_server.database import get_async_db
from argilla_server.api.policies.v1 import WebhookPolicy, authorize
from argilla_server.webhooks.v1.ping import notify_ping_event
from argilla_server.security import auth
from argilla_server.models import User
from argilla_server.api.schemas.v1.webhooks import (
    WebhookUpdate as WebhookUpdateSchema,
    WebhookCreate as WebhookCreateSchema,
    Webhooks as WebhooksSchema,
    Webhook as WebhookSchema,
)
from argilla_server.contexts import webhooks
from argilla_server.models import Webhook

router = APIRouter(tags=["webhooks"])


@router.get("/webhooks", response_model=WebhooksSchema)
async def list_webhooks(
    *,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Security(auth.get_current_user),
):
    await authorize(current_user, WebhookPolicy.list)

    return WebhooksSchema(items=await webhooks.list_webhooks(db))


@router.post("/webhooks", status_code=status.HTTP_201_CREATED, response_model=WebhookSchema)
async def create_webhook(
    *,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Security(auth.get_current_user),
    webhook_create: WebhookCreateSchema,
):
    await authorize(current_user, WebhookPolicy.create)

    return await webhooks.create_webhook(db, webhook_create.model_dump())


@router.patch("/webhooks/{webhook_id}", response_model=WebhookSchema)
async def update_webhook(
    *,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Security(auth.get_current_user),
    webhook_id: UUID,
    webhook_update: WebhookUpdateSchema,
):
    webhook = await Webhook.get_or_raise(db, webhook_id)

    await authorize(current_user, WebhookPolicy.update)

    return await webhooks.update_webhook(db, webhook, webhook_update.model_dump(exclude_unset=True))


@router.delete("/webhooks/{webhook_id}", response_model=WebhookSchema)
async def delete_webhook(
    *,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Security(auth.get_current_user),
    webhook_id: UUID,
):
    webhook = await Webhook.get_or_raise(db, webhook_id)

    await authorize(current_user, WebhookPolicy.delete)

    return await webhooks.delete_webhook(db, webhook)


@router.post("/webhooks/{webhook_id}/ping", status_code=status.HTTP_204_NO_CONTENT)
async def ping_webhook(
    *,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Security(auth.get_current_user),
    webhook_id: UUID,
):
    webhook = await Webhook.get_or_raise(db, webhook_id)

    await authorize(current_user, WebhookPolicy.ping)

    notify_ping_event(webhook)
