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

from unittest.mock import Mock, patch

import pytest
from argilla_v1.client.feedback.utils.assignment import (
    assign_records,
    assign_records_to_groups,
    assign_records_to_individuals,
    assign_workspaces,
    check_user,
    check_workspace,
)
from argilla_v1.client.users import User
from argilla_v1.client.workspaces import Workspace


@pytest.fixture
def mock_user():
    user = Mock(spec=User)
    user.username = "test_user"
    return user


@pytest.fixture
def mock_workspace():
    return Mock(spec=Workspace)


@pytest.fixture
def mock_check_user():
    def _mock(user_name):
        user = Mock(spec=User)
        user.username = user_name
        user.id = f"{user_name}_id"
        return user

    return _mock


@pytest.fixture
def mock_workspace_factory():
    def _factory(*args, **kwargs):
        mock = Mock(spec=Workspace)
        mock.users = []

        def create_mock_user(user_id):
            user_mock = Mock()
            user_mock.id = user_id
            return user_mock

        def add_user(user_id):
            # Check if a user with this ID already exists in the list
            if not any(user.id == user_id for user in mock.users):
                mock_user = create_mock_user(user_id)
                mock.users.append(mock_user)

        mock.add_user.side_effect = add_user

        return mock

    return _factory


@pytest.mark.parametrize(
    "input, exists, warning, is_user_obj",
    [("existing_user", True, False, False), ("new_user", False, True, False), (mock_user, True, False, True)],
)
@patch("argilla_v1.client.users.User.create")
@patch("argilla_v1.client.users.User.from_name")
def test_check_user(mock_from_name, mock_create, input, exists, warning, is_user_obj, mock_user):
    if is_user_obj:
        user_input = mock_user
    else:
        user_input = input
        if exists:
            mock_from_name.return_value = mock_user
        else:
            mock_from_name.side_effect = ValueError
            mock_create.return_value = mock_user

    result = check_user(user_input)

    assert result is mock_user

    if not exists and not is_user_obj:
        mock_create.assert_called_with(username=input, first_name=input, password="12345678", role="annotator")
    elif exists and not is_user_obj:
        mock_from_name.assert_called_with(input)


@pytest.mark.parametrize("workspace_name, workspace_exists", [("existing_workspace", True), ("new_workspace", False)])
@patch("argilla_v1.client.workspaces.Workspace.from_name")
@patch("argilla_v1.client.workspaces.Workspace.create")
def test_check_workspace(mock_create, mock_from_name, mock_workspace, workspace_name, workspace_exists):
    if workspace_exists:
        mock_from_name.return_value = mock_workspace
        mock_from_name.side_effect = None
    else:
        mock_from_name.side_effect = ValueError("Workspace does not exist.")
        mock_create.return_value = mock_workspace

    result = check_workspace(workspace_name)

    assert result is mock_workspace
    if workspace_exists:
        mock_from_name.assert_called_with(workspace_name)
    else:
        mock_create.assert_called_with(workspace_name)


@pytest.mark.parametrize(
    "overlap, shuffle, expected_error, expected_result",
    [
        (1, True, False, None),
        (1, False, False, None),
        (
            1,
            False,
            None,
            {
                "group1": {"user1": ["record1", "record4"], "user2": ["record1", "record4"]},
                "group2": {"user3": ["record2", "record5"], "user4": ["record2", "record5"]},
                "group3": {"user5": ["record3", "record6"]},
            },
        ),
        (
            2,
            False,
            None,
            {
                "group1": {
                    "user1": ["record1", "record3", "record4", "record6"],
                    "user2": ["record1", "record3", "record4", "record6"],
                },
                "group2": {
                    "user3": ["record1", "record2", "record4", "record5"],
                    "user4": ["record1", "record2", "record4", "record5"],
                },
                "group3": {"user5": ["record2", "record3", "record5", "record6"]},
            },
        ),
        (5, False, ValueError, None),
        (-1, False, ValueError, None),
    ],
)
@patch("argilla_v1.client.feedback.utils.assignment.random.shuffle")
def test_assign_records_to_groups(mock_shuffle, overlap, shuffle, expected_error, expected_result, mock_check_user):
    mock_groups = {"group1": ["user1", "user2"], "group2": ["user3", "user4"], "group3": ["user5"]}
    mock_records = ["record1", "record2", "record3", "record4", "record5", "record6"]

    with patch("argilla_v1.client.feedback.utils.assignment.check_user", side_effect=mock_check_user):
        if expected_error:
            with pytest.raises(expected_error):
                assign_records_to_groups(mock_groups, mock_records, overlap, shuffle)
        else:
            result = assign_records_to_groups(mock_groups, mock_records, overlap, shuffle)
            if expected_result is not None:
                assert result == expected_result

            if shuffle:
                mock_shuffle.assert_called_once_with(mock_records)
            else:
                mock_shuffle.assert_not_called()


@pytest.mark.parametrize(
    "overlap, shuffle, expected_error, expected_result",
    [
        (1, True, False, None),
        (1, False, False, None),
        (1, False, None, {"user1": ["record1", "record4"], "user2": ["record2", "record5"], "user3": ["record3"]}),
        (
            2,
            False,
            None,
            {
                "user1": ["record1", "record3", "record4"],
                "user2": ["record1", "record2", "record4", "record5"],
                "user3": ["record2", "record3", "record5"],
            },
        ),
        (5, False, ValueError, None),
        (-1, False, ValueError, None),
    ],
)
@patch("argilla_v1.client.feedback.utils.assignment.random.shuffle")
def test_assign_records_to_individuals(
    mock_shuffle, overlap, shuffle, expected_error, expected_result, mock_check_user
):
    mock_users = [f"user{i}" for i in range(1, 4)]
    mock_records = ["record1", "record2", "record3", "record4", "record5"]

    with patch("argilla_v1.client.feedback.utils.assignment.check_user", side_effect=mock_check_user):
        if expected_error:
            with pytest.raises(expected_error):
                assign_records_to_individuals(mock_users, mock_records, overlap, shuffle)
        else:
            result = assign_records_to_individuals(mock_users, mock_records, overlap, shuffle)
            if expected_result is not None:
                assert result == expected_result

            if shuffle:
                mock_shuffle.assert_called_once_with(mock_records)
            else:
                mock_shuffle.assert_not_called()


@pytest.mark.parametrize(
    "input, overlap, shuffle, expected_result",
    [
        (
            {"group1": ["user1", "user2"], "group2": ["user3"]},
            1,
            True,
            {"group1": {"user1": ["record1", "record2"], "user2": ["record3"]}, "group2": {"user3": ["record4"]}},
        ),
        (
            [f"user{i}" for i in range(1, 4)],
            0,
            False,
            {"user1": ["record1", "record4"], "user2": ["record2"], "user3": ["record3"]},
        ),
    ],
)
def test_assign_records(input, overlap, shuffle, expected_result):
    mock_records = ["record1", "record2", "record3", "record4", "record5"]

    def mock_assign_records_to_groups(users, records, overlap, shuffle):
        assert users == input
        assert records == mock_records
        assert overlap == overlap
        assert shuffle == shuffle
        return expected_result

    def mock_assign_records_to_individuals(users, records, overlap, shuffle):
        assert users == input
        assert records == mock_records
        assert overlap == overlap
        assert shuffle == shuffle
        return expected_result

    with patch(
        "argilla_v1.client.feedback.utils.assignment.assign_records_to_groups",
        side_effect=mock_assign_records_to_groups,
    ):
        with patch(
            "argilla_v1.client.feedback.utils.assignment.assign_records_to_individuals",
            side_effect=mock_assign_records_to_individuals,
        ):
            result = assign_records(input, mock_records, overlap, shuffle)
            assert result == expected_result


@pytest.mark.parametrize(
    "mock_assignments, assignment_type, expected_result",
    [
        (
            {
                "group1": {"user1": ["record1", "record3", "record5"], "user2": ["record1", "record3", "record5"]},
                "group2": {"user3": ["record2", "record4"]},
            },
            "group",
            {"group1": ["user1", "user2"], "group2": ["user3"]},
        ),
        (
            {
                "group1": {"user1": ["record1", "record3", "record5"], "user2": ["record1", "record3", "record5"]},
                "group2": {"user3": ["record2", "record4"]},
            },
            "group_personal",
            {"user1": ["user1"], "user2": ["user2"], "user3": ["user3"]},
        ),
        (
            {"user1": ["record1", "record4"], "user2": ["record2", "record5"], "user3": ["record3"]},
            "individual",
            {"user1": ["user1"], "user2": ["user2"], "user3": ["user3"]},
        ),
    ],
)
def test_assign_workspaces(mock_check_user, mock_workspace_factory, mock_assignments, assignment_type, expected_result):
    with patch("argilla_v1.client.feedback.utils.assignment.check_user", side_effect=mock_check_user):
        with patch(
            "argilla_v1.client.feedback.utils.assignment.User.from_id",
            side_effect=lambda user_id: Mock(username=user_id.split("_")[0]),
        ):
            with patch(
                "argilla_v1.client.feedback.utils.assignment.check_workspace", side_effect=mock_workspace_factory
            ):
                result = assign_workspaces(mock_assignments, assignment_type)
                assert result == expected_result
