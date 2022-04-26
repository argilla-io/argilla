import pytest

import rubrix as rb
from rubrix import settings
from rubrix.settings import TextClassificationSettings, TokenClassificationSettings


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
    settings.save_settings(dataset, settings=settings_)

    found_settings = settings.load_settings(dataset)
    assert found_settings == settings_

    with pytest.raises(
        ValueError, match="Provided settings are not compatible with dataset task."
    ):
        settings.save_settings(dataset, wrong_settings)
