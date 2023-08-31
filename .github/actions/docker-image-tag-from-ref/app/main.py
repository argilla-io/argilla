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
import re
from typing import Union

GITHUB_REF = os.environ["GITHUB_REF"]


def get_pull_request_number() -> Union[int, None]:
    match = re.match(r"refs/pull/(\d+)/merge", GITHUB_REF)
    if match:
        return int(match.group(1))
    return None


def get_branch_name() -> Union[str, None]:
    match = re.match(r"refs/heads/(.+)", GITHUB_REF)
    if match:
        return match.group(1)
    return None


def get_tag_name() -> Union[str, None]:
    match = re.match(r"refs/tags/(.+)", GITHUB_REF)
    if match:
        return match.group(1)
    return None


def clean_branch_name(branch_name: str) -> str:
    return re.sub(r"[^A-Za-z0-9\.]", "-", branch_name)


def get_docker_image_tag_from_reg() -> str:
    tag_name = get_tag_name()
    if tag_name:
        logging.info(f"`GITHUB_REF` refers to tag `{tag_name}`")
        return tag_name

    pr_number = get_pull_request_number()
    if pr_number:
        logging.info(f"`GITHUB_REF` refers to pull request #{pr_number}")
        docker_tag = f"pr-{pr_number}"
        return docker_tag

    branch_name = get_branch_name()
    if branch_name:
        logging.info(f"`GITHUB_REF` refers to branch `{branch_name}`")
        return clean_branch_name(branch_name)

    raise ValueError(f"Could not parse `GITHUB_REF` ({GITHUB_REF})")


def set_github_output(key: str, value: str) -> None:
    logging.info(f"Settings GitHub output: {key}={value}")
    with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
        print(f"{key}={value}", file=fh)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    docker_tag = get_docker_image_tag_from_reg()
    logging.info(f"Docker image tag: {docker_tag}")

    set_github_output("docker-image-tag", docker_tag)
