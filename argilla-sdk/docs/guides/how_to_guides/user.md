---
description: In this section, we will provide a step-by-step guide to show how to manage users and their credentials.
---

# User Management

This guide provides an overview of user roles and credentials, explaining how to set up and manage users in Argilla.

A **user** in Argilla is an authorized person, who depending on their role, can use the Python SDK and access the UI in a running Argilla instance. We differentiate between three types of users depending on their role, permissions and needs: `owner`, `admin` and `annotator`.

=== "Overview"
    |                    | Owner      | Admin                     | Annotator |
        |-------------------------------|------------|---------------------------|-----------|
        | **Number**                    | Unlimited  | Unlimited                 | Unlimited |
        | **Create and delete workspaces** | Yes      | No                        | No        |
        | **Assign users to workspaces** | Yes        | No                        | No        |
        | **Create, configure, update, and delete datasets** | Yes | Only within assigned workspaces | No |
        | **Create, update, and delete users** | Yes  | No                        | No        |
        | **Provide feedback with Argila UI** | Yes   | Yes   | Yes       |


=== "Owner"

    The `owner` refers to the root user who created the Argilla instance. Using workspaces within Argilla proves highly beneficial for organizing tasks efficiently. So, the owner has full access to all workspaces and their functionalities:

    - **Workspace management**: It can create, read and delete a workspace.
    - **User management**: It can create a new user, assign it to a workspace, and delete it. It can also list them and search for a specific one.
    - **Dataset management**: It can create, configure, retrieve, update, and delete datasets.
    - **Annotation**: It can annotate datasets in the Argilla UI.
    - **Feedback**: It can provide feedback with the Argilla UI.

=== "Admin"

    An `admin` user can only access the workspaces it has been assigned to and cannot assign other users to it. An admin user has the following permissions:

    - **Dataset management**: It can create, configure, retrieve, update, and delete datasets only on the assigned workspaces.
    - **Annotation**: It can annotate datasets in the assigned workspaces via the Argilla UI.
    - **Feedback**: It can provide feedback with the Argilla UI.

=== "Annotator"

    An `annotator` user is limited to accessing only the datasets assigned to it within the workspace. It has two specific permissions:

    - **Annotation**: It can annotate the assigned datasets in the Argilla UI.
    - **Feedback**: It can provide feedback with the Argilla UI.

??? Question "Question: Who can manage users?"

    Only users with the `owner` role can manage (create, retrieve, delete) other users.

## Default users and credentials

Argilla provides a default user with the `owner` role to help you get started in Python and the UI. The credentials for this user vary depending on the server configuration.

| Environment                   | Username | Password    | API Key        |
|-------------------------------|----------|-------------|----------------|
| Quickstart Docker and HF Space | owner    | 12345678    | owner.apikey   |
| Server image                  | argilla  | 1234        | argilla.apikey |

!!! info "Main Class"

    ```python
    rg.User(
        username="username",
        first_name="first_name",
        last_name="last_name",
        role="owner",
        password="password",
        client=client
    )
    ```
    > Check the [User - Python Reference](../../reference/argilla_sdk/users.md) to see the attributes, arguments, and methods of the `User` class in detail.

## Get current user

To ensure you're using the correct credentials for managing users, you can get the current user in Argilla using the `me` attribute of the `Argilla` class.

```python
import argilla_sdk as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

current_user = client.me
```

## Create a user

To create a new user in Argilla, you can define it in the `User` class and then call the `create` method. This method is inherited from the `Resource` base class and operates without modifications.

!!! info Password generation
    If you don't provide a password, a random one will be generated for you. Ensure you store this password securely by accessing it through `user.password` immediately after user creation. For security reasons, the password will not be retrievable later.

```python
import argilla_sdk as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

user_to_create = rg.User(
    username="my_username",
    password="12345678",
    client=client
)

created_user = user_to_create.create()
```
!!! tip "Accessing attributes"
    Access the attributes of a user by calling them directly on the `User` object. For example, `user.id` or `user.username`.

## List users

You can list all the existing users in Argilla by accessing the `users` attribute on the `Argilla` class and iterating over them. You can also use `len(client.users)` to get the number of users.

```python
import argilla_sdk as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

users = client.users

for user in users:
    print(user)
```
!!! tip "Notebooks"
    When using a notebook, executing `client.users` will display a table with `username`, `id`, `role`, and the last update as `updated_at`.

## Retrieve a user

You can retrieve an existing user from Argilla by accessing the `users` attribute on the `Argilla` class and passing the `username` as an argument.

```python
import argilla_sdk as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

retrieved_user = client.users("my_username")
```

## List users in a workspace

You can list all the users in a workspace by accessing the `users` attribute on the `Workspace` class and iterating over them. You can also use `len(workspace.users)` to get the number of users by workspace.

> For further information on how to manage workspaces, check this [how-to guide](workspace.md).

```python
import argilla_sdk as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

workspace = client.workspaces('my_workspace')

for user in workspace.users:
    print(user)
```

## Add a user to a workspace

You can add an existing user to a workspace in Argilla by calling the `add_to_workspace` method on the `User` class.

> For further information on how to manage workspaces, check this [how-to guide](workspace.md).

```python
import argilla_sdk as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

user = client.users('my_username')
workspace = client.workspaces('my_workspace')

added_user = user.add_to_workspace(workspace)
```

## Remove a user from a workspace

You can remove an existing user from a workspace in Argilla by calling the `remove_from_workspace` method on the `User` class.

> For further information on how to manage workspaces, check this [how-to guide](workspace.md).

```python
import argilla_sdk as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

user = client.users('my_username')
workspace = client.workspaces('my_workspace')

removed_user = user.remove_from_workspace(workspace)
```

## Delete a user

You can delete an existing user from Argilla by calling the `delete` method on the `User` class.

```python
import argilla_sdk as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

user_to_delete = client.users('my_username')

deleted_user = user_to_delete.delete()
```