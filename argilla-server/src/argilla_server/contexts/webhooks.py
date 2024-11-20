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

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.models import Webhook
from argilla_server.validators.webhooks import WebhookCreateValidator


async def list_webhooks(db: AsyncSession) -> Sequence[Webhook]:
    result = await db.execute(select(Webhook).order_by(Webhook.inserted_at.asc()))

    return result.scalars().all()


async def list_enabled_webhooks(db: AsyncSession) -> Sequence[Webhook]:
    result = await db.execute(select(Webhook).where(Webhook.enabled == True).order_by(Webhook.inserted_at.asc()))

    return result.scalars().all()


async def create_webhook(db: AsyncSession, webhook_attrs: dict) -> Webhook:
    webhook = Webhook(**webhook_attrs)

    await WebhookCreateValidator.validate(db, webhook)

    return await webhook.save(db)


async def update_webhook(db: AsyncSession, webhook: Webhook, webhook_attrs: dict) -> Webhook:
    return await webhook.update(db, **webhook_attrs)


async def delete_webhook(db: AsyncSession, webhook: Webhook) -> Webhook:
    return await webhook.delete(db)
