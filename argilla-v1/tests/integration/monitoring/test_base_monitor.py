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

from time import sleep
from typing import Any, Dict, List

from argilla_v1.client.api import Api
from argilla_v1.client.models import TextClassificationRecord
from argilla_v1.client.singleton import active_api
from argilla_v1.monitoring.base import BaseMonitor


def test_base_monitor_shutdown(mocked_client):
    class MockObj:
        pass

    class MockMonitor(BaseMonitor):
        def __init__(
            self,
            api: Api,
            dataset: str,
        ):
            super().__init__(
                MockObj(),
                api=api,
                dataset=dataset,
                log_interval=10,  # large time
            )
            self.records_sent = 0

        def _prepare_log_data(self, data: List[str]) -> Dict[str, Any]:
            return {
                "name": self.dataset,
                "records": [TextClassificationRecord(text=text) for text in data],
            }

    dataset = "test_base_monitor_shutdown"
    api = active_api()
    expected_number_of_records = 512
    monitor = MockMonitor(
        api=api,
        dataset=dataset,
    )

    api.delete(dataset)
    monitor.send_records(data=["this is a text"] * expected_number_of_records)
    monitor.shutdown()
    assert len(monitor._consumers) == 1
    for consumer in monitor._consumers.values():
        assert consumer.queue.unfinished_tasks == 0

    sleep(1)  # wait for refresh
    ds = api.load(dataset)
    assert len(ds) == expected_number_of_records
