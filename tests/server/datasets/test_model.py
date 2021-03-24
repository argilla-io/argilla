import pytest
from pydantic import ValidationError
from rubrix.server.datasets.model import CreationDatasetRequest


@pytest.mark.parametrize(
    "name",
    ["fine", "fine33", "fine_33", "fine-3-3"],
)
def test_dataset_naming_ok(name):
    request = CreationDatasetRequest(name=name)
    assert request.name == name


@pytest.mark.parametrize(
    "name",
    [
        "WrongName",
        "-wrong_name",
        "_wrong_name",
        "wrong_name-??",
        "wrong name",
        "wrong:name",
        "wrong=?name",
    ],
)
def test_dataset_naming_ko(name):
    with pytest.raises(ValidationError, match="string does not match regex"):
        CreationDatasetRequest(name=name)
