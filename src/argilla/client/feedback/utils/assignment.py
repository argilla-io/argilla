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


import random
from collections import defaultdict
from typing import Any, Dict, List, Union

from argilla.client.users import User
from argilla.client.workspaces import Workspace

# DOCS: Step 1: login argilla/ get all users (list/dict)/ get records


# Step 2: assign records
def assign_records_to_groups(
    groups: Dict[str, List[Any]], records: List[Any], overlap: int, shuffle: bool = True
) -> Dict[str, Dict[str, Any]]:
    """
    Assign records to predefined groups with controlled overlap (for the groups) and optional shuffle. All members of the same group will annotate the same records.

    Args:
        groups: A dictionary where keys are group names and values are lists of users.
        records: A list of records to be assigned.
        overlap: The number of times each record is assigned to consecutive groups (0 for no overlap).
        shuffle: If True, shuffle the records before assignment. Defaults to True.

    Returns:
        A dictionary where each key is a group and its value is another dictionary, which maps usernames to their respective assigned records.

    Raises:
        ValueError: If `overlap` is higher than the number of groups or negative.
    """
    if overlap < 0 or overlap >= len(groups.keys()):
        raise ValueError("Overlap must be less than the number of groups and must not be negative.")

    if shuffle:
        random.shuffle(records)

    assignments = {}
    assignments_grouped = {}
    group_names = list(groups.keys())
    num_groups = len(group_names)

    group_records = defaultdict(list)
    for idx, record in enumerate(records):
        for offset in range(overlap + 1):
            group_index = (idx + offset) % num_groups
            group_name = group_names[group_index]
            group_records[group_name].append(record)

    for group, users in groups.items():
        for user in users:
            assignments[user] = group_records[group]

        assignments_grouped[group] = {user.username: assignments.get(user, []) for user in users}

    return assignments_grouped


def assign_records_individuals(
    users: List[Any], records: List[Any], overlap: int, shuffle: bool = True
) -> Dict[str, List[Any]]:
    """
    Assign records to users with controlled overlap and optional shuffle.

    Args:
        users: A list of user objects, each with a 'username' attribute.
        records: A list of record objects to be assigned to users.
        overlap: The number of times each record is assigned to consecutive users (0 for no overlap).
        shuffle: If True, the records list will be shuffled before assignment. Defaults to True.

    Returns:
        A dictionary where keys are usernames and values are lists of assigned records.
    """
    if overlap < 0 or overlap >= len(users):
        raise ValueError("Overlap must be less than the number of users and must not be negative.")

    if shuffle:
        random.shuffle(records)

    assignments = {user.username: [] for user in users}
    num_users = len(users)

    for idx, record in enumerate(records):
        for offset in range(overlap + 1):
            user_index = (idx + offset) % num_users
            user = users[user_index].username
            assignments[user].append(record)

    return assignments


# Main function
def assign_records(
    users: Union[Dict[str, List[Any]], List[Any]], records: List[Any], overlap: int, shuffle: bool = True
) -> Union[Dict[str, List[Any]], Dict[str, Dict[str, Any]]]:
    """
    Assign records to either groups or individuals, with controlled overlap and optional shuffle.

    Args:
        users: Either a dictionary of groups or a list of individual user objects.
        records: A list of record objects to be assigned.
        overlap: The number of times each record is assigned to consecutive users or groups (0 for no overlap).
        shuffle: If True, the records list will be shuffled before assignment. Defaults to True.

    Returns:
        A dictionary where each key is a group and its value is another dictionary, which maps usernames to their respective assigned records.
        Or a dictionary where keys are usernames and values are lists of assigned records.
    """
    if isinstance(users, dict):
        return assign_records_to_groups(users, records, overlap, shuffle)
    elif isinstance(users, list):
        return assign_records_individuals(users, records, overlap, shuffle)


# Step 3: push dataset/s


def assign_workspaces(assignments, workspace_type):
    for group, users in assignments.items():
        if workspace_type == "group":
            workspace_name = group
            user_ids = [User.from_name(username).id for username in users.keys()]
        elif workspace_type == "group_personal":
            for username in users.keys():
                workspace_name = username
                user_ids = [User.from_name(username).id]
        elif workspace_type == "individual":
            workspace_name = group  # Here, 'group' is actually an individual's name
            user_ids = [User.from_name(workspace_name).id]

        # Check if the workspace exists and create it if not
        try:
            workspace = Workspace.from_name(workspace_name)
        except:
            workspace = Workspace.create(workspace_name)

        # Add users to the workspace
        for user_id in user_ids:
            workspace.add_user(user_id)


# DOCS:

# Tab1:

# For groups or individuals in common workspace

# fields = [...]
# questions = [...]
# guidelines = "..."
# etc.

# for assigned, records in assignments.items():
#     for record in records:
#         record.metadata['assigned'] = assigned
#         assigned_records.append(record)
# dataset = rg.FeedbackDataset(fields=fields, questions=questions, guidelines=guidelines)
# dataset.add_records(modified_records)
# remote_dataset = dataset.push_to_argilla(name="my_dataset"", workspace=workspace.name)

# Tab2:

# For groups, each group in a Workspace, each user in a group in a Workspace
# For individuals, each user in a Workspace

# assign_workspaces(assignments, workspace_type)

# for group, users in assignments.items():  # for user, records in assigments.items():
# dataset = rg.FeedbackDataset(fields=fields, questions=questions, guidelines=guidelines)
# dataset.add_records(records)
# remote_dataset = dataset.push_to_argilla(name="my_dataset"", workspace=workspace.name)

# for group, users in assignments.items():
#     for username, records in users.items():
# dataset = rg.FeedbackDataset(fields=fields, questions=questions, guidelines=guidelines)
# dataset.add_records(records)
# remote_dataset = dataset.push_to_argilla(name="my_dataset"", workspace=workspace.name)
