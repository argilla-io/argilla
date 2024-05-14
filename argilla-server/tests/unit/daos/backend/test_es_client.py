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
import os

import pytest
from argilla_server.commons.models import TaskType
from argilla_server.daos.backend import GenericElasticEngineBackend
from argilla_server.daos.backend.generic_elastic import dataset_records_index


@pytest.mark.skipif("GITHUB_RUN_ID" in os.environ, reason="This test fails often in GitHub actions")
def test_copy_index_as_alias(es: GenericElasticEngineBackend, opensearch):
    source_id = "source_id"
    source_id_alias = f"{source_id}_alias"
    target_id = "target_id"

    es.delete(source_id)
    es.delete(target_id)

    opensearch.indices.refresh()

    es.create_dataset(id=source_id, task=TaskType.text_classification)
    es.client.create_index_alias(
        index=dataset_records_index(source_id),
        alias=dataset_records_index(f"{source_id}_alias"),
    )

    assert es.get_schema(source_id) == es.get_schema(source_id_alias)

    es.copy(id_from=source_id_alias, id_to=target_id)
