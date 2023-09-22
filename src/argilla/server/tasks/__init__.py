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
from argilla.server.tasks.base import BackgroundTasks, IPCBackgroundTasksExecutor
from argilla.server.tasks.refresh_search_index import refresh_search_index

_background_tasks = None


def get_background_tasks() -> BackgroundTasks:
    global _background_tasks

    if not _background_tasks:
        _background_tasks = BackgroundTasks(IPCBackgroundTasksExecutor())

    return _background_tasks
