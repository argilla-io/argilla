# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import warnings
from threading import Lock
from typing import Optional
from huggingface_hub.utils._runtime import is_google_colab


_IS_GOOGLE_COLAB_CHECKED = False
_GOOGLE_COLAB_SECRET_LOCK = Lock()
_GOOGLE_COLAB_SECRET: Optional[dict] = None


def get_secret(name: str) -> Optional[str]:
    """
    Get secret if present

    Returns:
        `str` or `None`: The secret value, `None` if it doesn't exist.
    """
    return _get_secret_from_google_colab(name) or _get_secret_from_environment(name)


def _get_secret_from_environment(name: str) -> Optional[str]:
    """Get the secret  from the environment"""
    return _clean_secret_value(os.getenv(key=name))


def _get_secret_from_google_colab(name: str) -> Optional[str]:
    """Get token from Google Colab secrets vault using `google.colab.userdata.get(...)`.

    Token is read from the vault only once per session and then stored in a global variable to avoid re-requesting
    access to the vault.
    """
    # If it's not a Google Colab, fallback to environment variable
    if not is_google_colab():
        return None

    # `google.colab.userdata` is not thread-safe
    # This can lead to a deadlock if multiple threads try to access it at the same time
    # => use a lock
    # See https://github.com/huggingface/huggingface_hub/issues/1952 for more details.
    with _GOOGLE_COLAB_SECRET_LOCK:
        global _IS_GOOGLE_COLAB_CHECKED

        # we can add here some cache mechanism

        try:
            from google.colab import userdata
            from google.colab.errors import Error as ColabError
        except ImportError:
            return None

        try:
            # initialize to None in case of errors we evoid returning an undefined variable
            secret_value = None
            secret_value = _clean_secret_value(userdata.get(name))

        except userdata.NotebookAccessError:
            # Means the user has a secret call `ARGILLA_API_URL` and `ARGILLA_API_URL` and got a popup "please grand access to ARGILLA_API_URL" and refused it
            # => warn user but ignore error => do not re-request access to user
            if not _IS_GOOGLE_COLAB_CHECKED:
                warnings.warn(
                    f"\nAccess to the secret {name} has not been granted on this notebook."
                    "\nYou will not be requested again."
                    "\nPlease restart the session if you want to be prompted again."
                )
        except userdata.SecretNotFoundError:
            # Means the user did not define a name  secret => warn
            warnings.warn(f"\nThe secrets {name} and does not exist in your Colab secrets.")
        except ColabError as e:
            # Something happen but we don't know what => recommend to open a GitHub issue
            warnings.warn(
                f"\nError while fetching {name} secret value from your vault: '{str(e)}'."
                "\nYou are not authenticated with the Argilla in this notebook."
                "\nIf the error persists, please let us know by opening an issue on GitHub "
                "(https://github.com/argilla-io/argilla//issues/new)."
            )

        _IS_GOOGLE_COLAB_CHECKED = True

        return secret_value


def _clean_secret_value(value: Optional[str]) -> Optional[str]:
    """Clean token by removing trailing and leading spaces and newlines.

    If token is an empty string, return None.
    """
    if value is None:
        return None
    return value.replace("\r", "").replace("\n", "").strip() or None
