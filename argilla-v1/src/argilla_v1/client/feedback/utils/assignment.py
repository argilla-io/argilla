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
import warnings
from collections import defaultdict
from typing import Any, Dict, List, Union

from rich.progress import Progress

from argilla_v1.client.users import User
from argilla_v1.client.workspaces import Workspace


def check_user(user_to_check: Union[str, User]) -> User:
    """
    Helper function to check if the input is a User object. If it's a string, it attempts to retrieve the User object.
    If the User does not exist, it creates a new User with a default password and role.

    Args:
        user_to_check: a user object or a string that represents a username

    Returns:
        The User object corresponding to the input.
    """
    if isinstance(user_to_check, User):
        user = user_to_check
    else:
        try:
            user = User.from_name(user_to_check)
        except ValueError:
            user = User.create(username=user_to_check, first_name=user_to_check, password="12345678", role="annotator")
            warnings.warn(
                f"The user {user.username} was created with a default password. We recommend you to change it for security reasons.",
                UserWarning,
            )
    return user


def check_workspace(workspace_to_check: str) -> Workspace:
    """
    Helper function to check if the workspace exists. If it does not exist, it creates a new one.

    Args:
        workspace_to_check: a workspace string name

    Returns:
        The Workspace object corresponding to the input.
    """
    try:
        workspace = Workspace.from_name(workspace_to_check)
    except:
        workspace = Workspace.create(workspace_to_check)
    return workspace


def assign_records_to_groups(
    groups: Dict[str, List[Any]], records: List[Any], overlap: int, shuffle: bool = True
) -> Dict[str, Dict[str, Any]]:
    """
    Assign records to predefined groups with controlled overlap (for the groups) and optional shuffle. All members of the same group will annotate the same records.

    Args:
        groups: A dictionary where keys are group names and values are lists of users names or objects.
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

    if len(records) < len(groups.keys()):
        warnings.warn(
            "The number of groups is higher than the number of records. Some users will not be assigned any records.",
            UserWarning,
        )

    if shuffle:
        random.shuffle(records)

    assignments = {}
    assignments_grouped = {}
    group_names = list(groups.keys())
    num_groups = len(group_names)
    overlap = 1 if overlap == 0 else overlap

    group_records = defaultdict(list)
    with Progress() as progress:
        task = progress.add_task("[green]Processing records...", total=len(records))

        for idx, record in enumerate(records):
            for offset in range(overlap):
                group_index = (idx + offset) % num_groups
                group_name = group_names[group_index]
                group_records[group_name].append(record)

            progress.update(task, advance=1)

    for group, users in groups.items():
        users = [check_user(user) for user in users]
        for user in users:
            assignments[user] = group_records[group]

        assignments_grouped[group] = {user.username: assignments.get(user, []) for user in users}

    return assignments_grouped


def assign_records_to_individuals(
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

    Raises:
        ValueError: If `overlap` is higher than the number of users or negative.
    """
    if overlap < 0 or overlap >= len(users):
        raise ValueError("Overlap must be less than the number of users and must not be negative.")

    if len(records) < len(users):
        warnings.warn(
            "The number of users is higher than the number of records. Some users will not be assigned any records.",
            UserWarning,
        )

    if shuffle:
        random.shuffle(records)

    users = [check_user(user) for user in users]
    assignments = {user.username: [] for user in users}

    num_users = len(users)
    overlap = 1 if overlap == 0 else overlap

    with Progress() as progress:
        task = progress.add_task("[green]Processing records...", total=len(records))

        for idx, record in enumerate(records):
            for offset in range(overlap):
                user_index = (idx + offset) % num_users
                user = users[user_index].username
                assignments[user].append(record)

            progress.update(task, advance=1)

    return assignments


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

    Examples:
        >>> from argilla_v1.client.feedback.utils import assign_records
        >>> individual_assignments = assign_records([user1, user2, user3], records, 0, False)
        >>> group_assignments = assign_records({group1: [user1, user2], group2: [user3]}, records, 1, False)

    """
    if isinstance(users, dict):
        return assign_records_to_groups(users, records, overlap, shuffle)
    elif isinstance(users, list):
        return assign_records_to_individuals(users, records, overlap, shuffle)


def assign_workspaces(
    assignments: Union[Dict[str, List[Any]], Dict[str, Dict[str, Any]]], workspace_type: str
) -> Dict[str, List[Any]]:
    """
    Assign workspaces (and create them if needed) to either groups or individuals.

    Args:
        assignments: Either a dictionary of groups or a dictionary of users.
        workspace_type: Either 'group' (each group in a workspace), 'group_personal' (each member in a workspace) or 'individual' (each person in a workspace).

    Returns:
        A dictionary where each key is a workspace name and its value is a list of user names.

    Examples:
        >>> from argilla_v1.client.feedback.utils import assign_workspaces
        >>> wk_assignments = assign_workspaces(group_assignments, "group")
        >>> wk_assignments = assign_workspaces(group_assignments, "group_personal")
        >>> wk_assignments = assign_workspaces(individual_assignments, "individual")

    """
    wk_assignments = {}

    for group, users in assignments.items():
        if workspace_type == "group":
            workspace_name = group
            user_ids = [check_user(user).id for user in users.keys()]

        elif workspace_type == "group_personal":
            for user in users.keys():
                workspace_name = user
                user_ids = [check_user(user).id]
                workspace = check_workspace(workspace_name)

                for user_id in user_ids:
                    try:
                        workspace.add_user(user_id)
                    except:
                        pass

                wk_assignments[workspace_name] = [User.from_id(user.id).username for user in workspace.users]

            continue

        elif workspace_type == "individual":
            workspace_name = group
            user_ids = [check_user(group).id]

        workspace = check_workspace(workspace_name)

        for user_id in user_ids:
            try:
                workspace.add_user(user_id)
            except:
                pass

        wk_assignments[workspace_name] = [User.from_id(user.id).username for user in workspace.users]

    return wk_assignments
