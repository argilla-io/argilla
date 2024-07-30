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
                "Milestone": [],
                "Reactions": [],
                "Comments": [],
                "URL": [],
                "Author": [],
                "Author association": [],
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
                if "pull_request" in issue:
                    continue
                issues_data.append(
                    {
                        "Issue": f"{issue['number']} - {issue['title']}",
                        "State": issue["state"],
                        "Created at": issue["created_at"],
                        "Milestone": (issue.get("milestone") or {}).get("title"),
                        "Reactions": issue["reactions"]["total_count"],
                        "Comments": issue["comments"],
                        "URL": issue["html_url"],
                        "Author": issue["user"]["login"],
                        "Author association": issue["author_association"],
                    }
                )

            issues_url = response.links.get("next", {}).get("url", None)

    return pd.DataFrame(issues_data)


with mkdocs_gen_files.open(DATA_PATH, "w") as f:
    df = fetch_data_from_github(REPOSITORY, GITHUB_ACCESS_TOKEN)

    df["Milestone"] = df["Milestone"].astype(str).fillna("")
    planned_issues = df[
        ((df["Milestone"].str.startswith("v2")) & (df["State"] == "open"))
        | ((df["Milestone"].str.startswith("2")) & (df["State"] == "open"))
    ]
    open_issues = df.loc[df["State"] == "open"]
    engagement_df = (
        open_issues[["URL", "Issue", "Reactions", "Comments"]]
        .sort_values(by=["Reactions", "Comments"], ascending=False)
        .head(10)
        .reset_index()
    )

    community_issues = df[df["Author association"] != "MEMBER"]
    community_issues_df = (
        community_issues[["URL", "Issue", "Created at", "Author", "State"]]
        .sort_values(by=["Created at"], ascending=False)
        .head(10)
        .reset_index()
    )

    df["Milestone"] = df["Milestone"].astype(str).fillna("")
    planned_issues = df[
        ((df["Milestone"].str.startswith("v2")) & (df["State"] == "open"))
        | ((df["Milestone"].str.startswith("2")) & (df["State"] == "open"))
    ]
    planned_issues_df = (
        planned_issues[["URL", "Issue", "Created at", "Milestone", "State"]]
        .sort_values(by=["Milestone"], ascending=True)
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
