import pytest
from PIL import Image
from argilla.media import pil_to_data_uri


def test_pil_to_data_uri_with_valid_image():
    image = Image.new("RGB", (100, 100), color="red")
    data_uri = pil_to_data_uri(image)
    assert isinstance(data_uri, str)
    assert data_uri.startswith("data:image/png;base64,")


def test_pil_to_data_uri_with_invalid_image():
    image = "not an image"
    with pytest.raises(ValueError):
        pil_to_data_uri(image)
