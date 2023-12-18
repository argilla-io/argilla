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

from redis import Redis
from rq import Queue

# TODO: We should set the Redis connection using environment variables
redis_connection = Redis()

# NOTE: Regular default queue using Redis
default_queue = Queue(connection=redis_connection)

# NOTE: Synchronous default queue without using Redis (using fakeredis)
# from fakeredis import FakeStrictRedis
# default_queue = Queue(name="default", connection=FakeStrictRedis(), is_async=False)

# NOTE: To execute worker consuming default queue:
# $ rq worker --with-scheduler
# To execute worker consuming default and other-queue
# $ rq worker --with-scheduler default other-queue
