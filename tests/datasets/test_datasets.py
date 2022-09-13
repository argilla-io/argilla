import pytest

import rubrix as rb
from rubrix import TextClassificationSettings, TokenClassificationSettings
from rubrix.client import api
from rubrix.client.sdk.commons.errors import ForbiddenApiError


@pytest.mark.parametrize(
    ("settings_", "wrong_settings"),
    [
        (
            TextClassificationSettings(label_schema={"A", "B"}),
            TokenClassificationSettings(label_schema={"PER", "ORG"}),
        ),
        (
            TokenClassificationSettings(label_schema={"PER", "ORG"}),
            TextClassificationSettings(label_schema={"A", "B"}),
        ),
    ],
)
def test_settings_workflow(mocked_client, settings_, wrong_settings):
    dataset = "test-dataset"
    rb.delete(dataset)
    rb.configure_dataset(dataset, settings=settings_)

    current_api = api.active_api()
    datasets_api = current_api.datasets

    found_settings = datasets_api.load_settings(dataset)
    assert found_settings == settings_

    settings_.label_schema = {"LALALA"}
    rb.configure_dataset(dataset, settings_)

    found_settings = datasets_api.load_settings(dataset)
    assert found_settings == settings_

    with pytest.raises(ValueError, match="Task type mismatch"):
        rb.configure_dataset(dataset, wrong_settings)


def test_delete_dataset_by_non_creator(mocked_client):
    try:
        dataset = "test_delete_dataset_by_non_creator"
        rb.delete(dataset)
        rb.configure_dataset(
            dataset, settings=TextClassificationSettings(label_schema={"A", "B", "C"})
        )
        mocked_client.change_current_user("mock-user")
        with pytest.raises(ForbiddenApiError):
            rb.delete(dataset)
    finally:
        mocked_client.reset_default_user()
