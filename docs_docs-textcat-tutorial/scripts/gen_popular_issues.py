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
from datetime import datetime

import mkdocs_gen_files
import pandas as pd
import requests

REPOSITORY = "argilla-io/argilla"
DATA_PATH = "community/popular_issues.md"

GITHUB_ACCESS_TOKEN = os.getenv("GH_ACCESS_TOKEN")  # public_repo and read:org scopes are required


def fetch_data_from_github(repository, auth_token):
    if auth_token is None:
        return pd.DataFrame(
            {
                "Issue": [],
                "State": [],
                "Created at": [],
                "Closed at": [],
                "Last update": [],
                "Labels": [],
                "Milestone": [],
                "Reactions": [],
                "Comments": [],
                "URL": [],
                "Repository": [],
                "Author": [],
            }
        )
    headers = {"Authorization": f"token {auth_token}", "Accept": "application/vnd.github.v3+json"}
    issues_data = []

    print(f"Fetching issues from {repository}...")
    with requests.Session() as session:
        session.headers.update(headers)

        owner, repo_name = repository.split("/")
        issues_url = f"https://api.github.com/repos/{owner}/{repo_name}/issues?state=all"

        while issues_url:
            response = session.get(issues_url)
            issues = response.json()

            for issue in issues:
                issues_data.append(
                    {
                        "Issue": f"{issue['number']} - {issue['title']}",
                        "State": issue["state"],
                        "Created at": issue["created_at"],
                        "Closed at": issue.get("closed_at", None),
                        "Last update": issue["updated_at"],
                        "Labels": [label["name"] for label in issue["labels"]],
                        "Milestone": (issue.get("milestone") or {}).get("title"),
                        "Reactions": issue["reactions"]["total_count"],
                        "Comments": issue["comments"],
                        "URL": issue["html_url"],
                        "Repository": repo_name,
                        "Author": issue["user"]["login"],
                    }
                )

            issues_url = response.links.get("next", {}).get("url", None)

    return pd.DataFrame(issues_data)


def get_org_members(auth_token):
    headers = {"Authorization": f"token {auth_token}", "Accept": "application/vnd.github.v3+json"}
    members_list = []

    members_url = "https://api.github.com/orgs/argilla-io/members"

    if auth_token is None:
        return []

    while members_url:
        response = requests.get(members_url, headers=headers)
        members = response.json()

        for member in members:
            members_list.append(member["login"])

        members_list.extend(["pre-commit-ci[bot]"])

        members_url = response.links.get("next", {}).get("url", None)

    return members_list


with mkdocs_gen_files.open(DATA_PATH, "w") as f:
    df = fetch_data_from_github(REPOSITORY, GITHUB_ACCESS_TOKEN)

    open_issues = df.loc[df["State"] == "open"]
    engagement_df = (
        open_issues[["URL", "Issue", "Repository", "Reactions", "Comments"]]
        .sort_values(by=["Reactions", "Comments"], ascending=False)
        .head(10)
        .reset_index()
    )

    members = get_org_members(GITHUB_ACCESS_TOKEN)
    community_issues = df.loc[~df["Author"].isin(members)]
    community_issues_df = (
        community_issues[["URL", "Issue", "Repository", "Created at", "Author", "State"]]
        .sort_values(by=["Created at"], ascending=False)
        .head(10)
        .reset_index()
    )

    planned_issues = df.loc[df["Milestone"].notna()]
    planned_issues_df = (
        planned_issues[["URL", "Issue", "Repository", "Created at", "Milestone", "State"]]
        .sort_values(by=["Milestone"], ascending=False)
        .head(10)
        .reset_index()
    )

    f.write('=== "Most engaging open issues"\n\n')
    f.write("    | Rank | Issue | Reactions | Comments |\n")
    f.write("    |------|-------|:---------:|:--------:|\n")
    for ix, row in engagement_df.iterrows():
        f.write(f"    | {ix+1} | [{row['Issue']}]({row['URL']}) | 👍 {row['Reactions']} | 💬 {row['Comments']} |\n")

    f.write('\n=== "Latest issues open by the community"\n\n')
    f.write("    | Rank | Issue | Author |\n")
    f.write("    |------|-------|:------:|\n")
    for ix, row in community_issues_df.iterrows():
        state = "🟢" if row["State"] == "open" else "🟣"
        f.write(f"    | {ix+1} | {state} [{row['Issue']}]({row['URL']}) | by **{row['Author']}** |\n")

    f.write('\n=== "Planned issues for upcoming releases"\n\n')
    f.write("    | Rank | Issue | Milestone |\n")
    f.write("    |------|-------|:------:|\n")
    for ix, row in planned_issues_df.iterrows():
        state = "🟢" if row["State"] == "open" else "🟣"
        f.write(f"    | {ix+1} | {state} [{row['Issue']}]({row['URL']}) |  **{row['Milestone']}** |\n")

    today = datetime.today().date()
    f.write(f"\nLast update: {today}\n")
