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

import base64
import hashlib
import logging
import os
from typing import Any, Dict

SECRET = os.environ.get("ENVIRONMENT_CREDENTIALS_SECRET")
GITHUB_REF = os.environ.get("GITHUB_REF")


def generate_password_from_secret(secret: str, salt: str, length: int = 16) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", secret.encode(), salt.encode(), 100000)
    password = base64.urlsafe_b64encode(dk).decode("utf-8")
    password = "".join(char for char in password if char.isalnum())
    return password[:length]


def generate_credentials() -> Dict[str, Any]:
    credentials = {}
    for user in ["owner", "admin", "annotator"]:
        logging.info(f"Generating random credential for user '{user}'")
        password = generate_password_from_secret(
            secret=SECRET, salt=f"{GITHUB_REF}/{user}", length=32
        )
        credentials[user] = password
    return credentials


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if not SECRET:
        logging.error("`ENVIRONMENT_CREDENTIALS_SECRET` secret is not set!")
        raise KeyError("`ENVIRONMENT_CREDENTIALS_SECRET` secret is not set")

    credentials = generate_credentials()

    with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
        for key, value in credentials.items():
            print(f"::add-mask::{value}")
            print(f"{key}={value}", file=fh)
