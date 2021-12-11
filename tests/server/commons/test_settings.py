import os

import pytest
from pydantic import ValidationError

from rubrix.server.commons.settings import ApiSettings


@pytest.mark.parametrize("bad_namespace", ["Badns", "bad-ns", "12-bad-ns", "@bad"])
def test_wrong_settings_namespace(bad_namespace):
    os.environ["RUBRIX_NAMESPACE"] = bad_namespace
    with pytest.raises(ValidationError):
        ApiSettings()


def test_settings_namespace():
    os.environ["RUBRIX_NAMESPACE"] = "namespace"
    settings = ApiSettings()

    assert settings.namespace == "namespace"
    assert settings.dataset_index_name == ".rubrix.namespace.datasets-v0"
    assert (
        settings.dataset_records_index_name == ".rubrix.namespace.dataset.{}.records-v0"
    )
