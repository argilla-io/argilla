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
import re
import string
from typing import Any, Dict, Union

from slack_sdk import WebClient

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
GITHUB_REF = os.environ["GITHUB_REF"]

# Inputs
SLACK_CHANNEL_NAME = os.environ.get("INPUT_SLACK-CHANNEL-NAME")
URL = os.environ.get("INPUT_URL")
OWNER = os.environ.get("INPUT_OWNER")
ADMIN = os.environ.get("INPUT_ADMIN")
ANNOTATOR = os.environ.get("INPUT_ANNOTATOR")


def get_pull_request_number() -> Union[int, None]:
    match = re.match(r"refs/pull/(\d+)/merge", GITHUB_REF)
    if match:
        return int(match.group(1))
    return None


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


def get_slack_client() -> WebClient:
    if SLACK_BOT_TOKEN is None:
        logging.error("`SLACK_BOT_TOKEN` secret is not set!")
        raise KeyError("`SLACK_BOT_TOKEN` secret is not set")
    return WebClient(token=SLACK_BOT_TOKEN)


def get_bot_id(client: WebClient) -> str:
    response = client.auth_test()
    response.validate()
    return response["bot_id"]


def get_slack_channel_id(client: WebClient) -> Union[str, None]:
    response = client.conversations_list()
    response.validate()
    for result in response:
        for channel in result["channels"]:
            if channel["name"] == SLACK_CHANNEL_NAME:
                channel_id = channel["id"]
                logging.info(
                    f"Found channel id for '{SLACK_CHANNEL_NAME}' channel: '{channel_id}'"
                )
                return channel_id


def join_slack_channel(client: WebClient, channel_id: str) -> None:
    response = client.conversations_join(channel=channel_id)
    response.validate()


def get_pr_url(pr_number: int) -> str:
    return f"https://github.com/argilla-io/argilla/pull/{pr_number}"


def get_thread_ts_pr_message(
    client: WebClient, channel_id: str, pr_number: int
) -> Union[str, None]:
    response = client.conversations_history(channel=channel_id, limit=1000)
    response.validate()

    pr_url = get_pr_url(pr_number)

    for message in response["messages"]:
        if "attachments" in message:
            pr_attachment = message["attachments"][0]
            title = pr_attachment.get("title")
            callback_id = pr_attachment.get("callback_id")
            if not title or not callback_id:
                continue
            if pr_url in title and callback_id == "pr-opened-interaction":
                return message["ts"]

    return None


def bot_already_replied(client: WebClient, channel_id: str, thread_ts: str) -> bool:
    response = client.conversations_replies(channel=channel_id, ts=thread_ts)
    response.validate()

    slack_bot_id = get_bot_id(client)

    for message in response["messages"]:
        if "bot_id" in message and message["bot_id"] == slack_bot_id:
            return True

    return False


def reply_thread_with_credentials(
    client: WebClient, channel_id: str, thread_ts: str
) -> None:
    client.chat_postMessage(
        channel=channel_id,
        text=f"Credentials for PR deployed environment (use as password and API key):\n- URL: {URL}\n- owner: '{OWNER}'\n- admin: '{ADMIN}'\n- annotator: '{ANNOTATOR}'",
        thread_ts=thread_ts,
    ).validate()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if SLACK_CHANNEL_NAME is None:
        logging.error("`slack-channel-name` input is not set!")
        raise KeyError("`slack-channel-name` input is not set")

    if URL is None:
        logging.error("`url` input is not set!")
        raise KeyError("`url` input is not set")

    if OWNER is None:
        logging.error("`owner` input is not set!")
        raise KeyError("`owner` input is not set")

    if ADMIN is None:
        logging.error("`admin` input is not set!")
        raise KeyError("`admin` input is not set")

    if ANNOTATOR is None:
        logging.error("`annotator` input is not set!")
        raise KeyError("`annotator` input is not set")

    pr_number = get_pull_request_number()
    if pr_number is None:
        logging.error(f"Could not parse `GITHUB_REF` ({GITHUB_REF}) to get PR number")
        raise ValueError(
            f"Could not parse `GITHUB_REF` ({GITHUB_REF}) to get PR number"
        )

    client = get_slack_client()

    channel_id = get_slack_channel_id(client)
    if channel_id is None:
        logging.error(f"Could not find channel '{SLACK_CHANNEL_NAME}'")
        raise ValueError(f"Could not find channel '{SLACK_CHANNEL_NAME}'")

    join_slack_channel(client, channel_id)

    thread_ts = get_thread_ts_pr_message(client, channel_id, pr_number)
    if not thread_ts:
        logging.error(f"Could not find message for PR {pr_number}")
        raise ValueError(f"Could not find message for PR {pr_number}")

    if bot_already_replied(client, channel_id, thread_ts):
        logging.info(f"Bot already replied to thread of PR {pr_number}")
    else:
        reply_thread_with_credentials(client, channel_id, thread_ts)
