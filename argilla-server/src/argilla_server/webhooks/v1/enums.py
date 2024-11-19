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

try:
    from enum import StrEnum
except ImportError:
    from enum import Enum

    class StrEnum(str, Enum):
        """Custom StrEnum class for Python <3.11 compatibility."""

        def __str__(self):
            return str(self.value)


class WebhookEvent(StrEnum):
    dataset_created = "dataset.created"
    dataset_updated = "dataset.updated"
    dataset_deleted = "dataset.deleted"
    dataset_published = "dataset.published"

    record_created = "record.created"
    record_updated = "record.updated"
    record_deleted = "record.deleted"
    record_completed = "record.completed"

    response_created = "response.created"
    response_updated = "response.updated"
    response_deleted = "response.deleted"


class DatasetEvent(StrEnum):
    created = WebhookEvent.dataset_created.value
    updated = WebhookEvent.dataset_updated.value
    deleted = WebhookEvent.dataset_deleted.value
    published = WebhookEvent.dataset_published.value


class RecordEvent(StrEnum):
    created = WebhookEvent.record_created.value
    updated = WebhookEvent.record_updated.value
    deleted = WebhookEvent.record_deleted.value
    completed = WebhookEvent.record_completed.value


class ResponseEvent(StrEnum):
    created = WebhookEvent.response_created.value
    updated = WebhookEvent.response_updated.value
    deleted = WebhookEvent.response_deleted.value
