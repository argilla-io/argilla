from typing import TYPE_CHECKING
import io
import base64

if TYPE_CHECKING:
    from PIL import Image


def pil_to_data_uri(image_object: "Image") -> str:
    """Convert a PIL image to a base64 data URI string.
    Parameters:
        image_object (Image): The PIL image to convert to a base64 data URI.
    Returns:
        str: The data URI string.
    """
    try:
        from PIL import Image
    except ImportError as e:
        raise ImportError("The PIL library is required to convert PIL images for upload.") from e

    if not isinstance(image_object, Image.Image):
        raise ValueError("The image_object must be a PIL Image object.")

    try:
        buffered = io.BytesIO()
        image_object.save(buffered, format="PNG")
    except Exception as e:
        raise ValueError("An error occurred while saving the image binary to buffer") from e

    try:
        img_str = base64.b64encode(buffered.getvalue()).decode()
        data_uri = f"data:image/png;base64,{img_str}"
    except Exception as e:
        raise ValueError("An error occurred while converting the image binary to base64") from e

    return data_uri
