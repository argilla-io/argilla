import pytest

import rubrix as rb
from rubrix import TextClassificationSettings, TokenClassificationSettings
from rubrix.client import api
from rubrix.client.sdk.commons.errors import AlreadyExistsApiError


@pytest.mark.parametrize(
    ("settings_", "wrong_settings"),
    [
        (
            TextClassificationSettings(labels_schema={"A", "B"}),
            TokenClassificationSettings(labels_schema={"PER", "ORG"}),
        ),
        (
            TokenClassificationSettings(labels_schema={"PER", "ORG"}),
            TextClassificationSettings(labels_schema={"A", "B"}),
        ),
    ],
)
def test_settings_workflow(mocked_client, settings_, wrong_settings):
    dataset = "test-dataset"
    rb.delete(dataset)
    rb.create_dataset(dataset, settings=settings_)

    current_api = api.active_api()
    datasets_api = current_api.datasets

    found_settings = datasets_api.load_settings(dataset)
    assert found_settings == settings_

    with pytest.raises(AlreadyExistsApiError):
        rb.create_dataset(dataset, settings_)

    with pytest.raises(AlreadyExistsApiError):
        rb.create_dataset(dataset, wrong_settings)
