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

import base64
import os

import mkdocs_gen_files
import requests

REPOSITORY = "argilla-io/argilla"
CHANGELOG_PATH = "argilla/CHANGELOG.md"
RETRIEVED_BRANCH = "develop"

DATA_PATH = "community/changelog.md"

GITHUB_ACCESS_TOKEN = os.getenv("GH_ACCESS_TOKEN")  # public_repo and read:org scopes are required


def fetch_file_from_github(repository, changelog_path, branch, auth_token):
    if auth_token is None:
        return ""
    headers = {"Authorization": f"Bearer {auth_token}", "Accept": "application/vnd.github.v3+json"}

    owner, repo_name = repository.split("/")
    changelog_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{changelog_path}?ref={branch}"

    print(f"Fetching CHANGELOG.md from {changelog_url}...")
    response = requests.get(changelog_url, headers=headers)

    content = base64.b64decode(response.json()["content"]).decode("utf-8")

    return content


with mkdocs_gen_files.open(DATA_PATH, "w") as f:
    content = fetch_file_from_github(REPOSITORY, CHANGELOG_PATH, RETRIEVED_BRANCH, GITHUB_ACCESS_TOKEN)
    f.write(content)
