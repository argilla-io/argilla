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

import redis

from rq import Queue

from argilla_server.settings import settings

REDIS_CONNECTION = redis.from_url(settings.redis_url)

DEFAULT_QUEUE = Queue("default", connection=REDIS_CONNECTION)
HIGH_QUEUE = Queue("high", connection=REDIS_CONNECTION)

JOB_TIMEOUT_DISABLED = -1
