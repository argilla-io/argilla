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

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from argilla_server.models import Webhook
from argilla_server.api.webhooks.v1.ping import notify_ping_event


async def ping_webhook(webhook: Webhook) -> None:
    notify_ping_event(webhook)


async def list_webhooks(db: AsyncSession) -> Sequence[Webhook]:
    return (await db.execute(select(Webhook).order_by(Webhook.inserted_at.asc()))).scalars().all()


async def create_webhook(db: AsyncSession, webhook_attrs: dict) -> Webhook:
    return await Webhook(**webhook_attrs).save(db)


async def update_webhook(db: AsyncSession, webhook: Webhook, webhook_attrs: dict) -> Webhook:
    return await webhook.update(db, **webhook_attrs)


async def delete_webhook(db: AsyncSession, webhook: Webhook) -> Webhook:
    return await webhook.delete(db)
