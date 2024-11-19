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

import pytest

from tests.factories import WebhookFactory


@pytest.mark.asyncio
class TestWebhook:
    async def test_secret_is_generated_by_default(self):
        webhook = await WebhookFactory.create()

        assert webhook.secret

    async def test_secret_is_generated_by_default_individually(self):
        webhooks = await WebhookFactory.create_batch(2)

        assert webhooks[0].secret != webhooks[1].secret
