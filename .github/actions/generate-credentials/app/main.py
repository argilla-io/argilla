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

import logging
import os
import random
import string
from typing import Any, Dict


def generate_random_string(length: int, include_uppercase: bool = True) -> str:
    characters = string.ascii_letters
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string


def generate_credentials() -> Dict[str, Any]:
    credentials = {}
    for user in ["owner", "admin", "annotator"]:
        logging.info(f"Generating random credential for user '{user}'")
        password = generate_random_string(16)
        credentials[user] = password
    return credentials


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    credentials = generate_credentials()

    with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
        for key, value in credentials:
            print(f"::add-mask::{value}")
            print(f"{key}={value}", file=fh)
