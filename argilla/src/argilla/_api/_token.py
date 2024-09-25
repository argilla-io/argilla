import os
import warnings
from threading import Lock
from typing import Optional
from huggingface_hub.utils import is_google_colab, is_colab_enterprise
from argilla._constants import _DEFAULT_API_URL


_IS_GOOGLE_COLAB_CHECKED = False
_GOOGLE_COLAB_SECRET_LOCK = Lock()
_GOOGLE_COLAB_SECRET: Optional[dict] = None


def get_token() -> Optional[dict]:
    """
    Get token if present

    Returns:
        `dict` or `None`: The token, `None` if it doesn't exist.
    """
    return _get_token_from_google_colab() or _get_token_from_environment()


def _get_token_from_environment() -> Optional[str]:
    ARGILLA_API_URL = _clean_token(os.getenv(key="ARGILLA_API_URL", default=_DEFAULT_API_URL))
    ARGILLA_API_KEY = _clean_token(os.getenv(key="ARGILLA_API_KEY"))
    return {"ARGILLA_API_URL": ARGILLA_API_URL, "ARGILLA_API_KEY": ARGILLA_API_KEY}


def _get_token_from_google_colab() -> Optional[str]:
    """Get token from Google Colab secrets vault using `google.colab.userdata.get(...)`.

    Token is read from the vault only once per session and then stored in a global variable to avoid re-requesting
    access to the vault.
    """
    # If it's not a Google Colab or it's Colab Enterprise, fallback to environment variable or token file authentication
    if not is_google_colab() or is_colab_enterprise():
        return None

    # `google.colab.userdata` is not thread-safe
    # This can lead to a deadlock if multiple threads try to access it at the same time
    # => use a lock
    # See https://github.com/huggingface/huggingface_hub/issues/1952 for more details.
    with _GOOGLE_COLAB_SECRET_LOCK:
        global _GOOGLE_COLAB_SECRET
        global _IS_GOOGLE_COLAB_CHECKED

        if _IS_GOOGLE_COLAB_CHECKED:  # request access only once
            return _GOOGLE_COLAB_SECRET

        try:
            from google.colab import userdata
            from google.colab.errors import Error as ColabError
        except ImportError:
            return None

        try:
            ARGILLA_API_URL = userdata.get("ARGILLA_API_URL")
            ARGILLA_API_KEY = userdata.get("ARGILLA_API_KEY")

            _GOOGLE_COLAB_SECRET = {
                "ARGILLA_API_URL": _clean_token(ARGILLA_API_URL),
                "ARGILLA_API_KEY": _clean_token(ARGILLA_API_KEY),
            }

        except userdata.NotebookAccessError:
            # Means the user has a secret call `HF_TOKEN` and got a popup "please grand access to HF_TOKEN" and refused it
            # => warn user but ignore error => do not re-request access to user
            warnings.warn(
                "\nAccess to the secret `ARGILLA_API_URL` and `ARGILLA_API_KEY` has not been granted on this notebook."
                "\nYou will not be requested again."
                "\nPlease restart the session if you want to be prompted again."
            )
            _GOOGLE_COLAB_SECRET = None
        except userdata.SecretNotFoundError:
            # Means the user did not define a `ARGILLA_API_URL` and `ARGILLA_API_KEY` secret => warn
            warnings.warn("\nThe secrets `ARGILLA_API_URL` and`ARGILLA_API_KEY` do not exist in your Colab secrets.")
            _GOOGLE_COLAB_SECRET = None
        except ColabError as e:
            # Something happen but we don't know what => recommend to open a GitHub issue
            warnings.warn(
                f"\nError while fetching `ARGILLA_API_URL` and `ARGILLA_API_KEY` secret value from your vault: '{str(e)}'."
                "\nYou are not authenticated with the Argilla in this notebook."
                "\nIf the error persists, please let us know by opening an issue on GitHub "
                "(https://github.com/argilla-io/argilla//issues/new)."
            )
            _GOOGLE_COLAB_SECRET = None

        _IS_GOOGLE_COLAB_CHECKED = True
        return _GOOGLE_COLAB_SECRET


def _clean_token(token: Optional[str]) -> Optional[str]:
    """Clean token by removing trailing and leading spaces and newlines.

    If token is an empty string, return None.
    """
    if token is None:
        return None
    return token.replace("\r", "").replace("\n", "").strip() or None
