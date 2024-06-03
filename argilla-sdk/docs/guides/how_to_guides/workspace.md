---
description: In this section, we will provide a step-by-step guide to show how to manage workspaces.
---

# Workspace Management

This guide provides an overview of workspaces, explaining how to set up and manage workspaces in Argilla.

A **workspace** is a *space* inside your Argilla instance where authorized users can collaborate on datasets. It is accessible through the Python SDK and the UI.

??? Question "Question: Who can manage workspaces?"

    Only users with the `owner` role can manage (create, read and delete) workspaces.

    A user with the `admin` role can only read the workspace to which it belongs.

## Default workspaces

Argilla provides a default workspace to help you get started in Python and the UI. The name of this workspace varies depending on the server configuration.

| Environment                   | Name |
|-------------------------------|----------|
| Quickstart Docker and HF Space | admin    |
| Server image                  | argilla  |

!!! info "Main Class"

    ```python
    rg.Workspace(
        name = "name",
        client=client
    )
    ```
    > Check the [Workspace - Python Reference](../../reference/argilla_sdk/workspaces.md) to see the attributes, arguments, and methods of the `Workspace` class in detail.

## Create a new workspace

To create a new workspace in Argilla, you can define it in the `Workspace` class and then call the `create` method. This method is inherited from the `Resource` base class and operates without modifications.

> When you create a new workspace, it will be empty. To create and add a new dataset, check these [guides](dataset.md).

```python
import argilla_sdk as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

workspace_to_create = rg.Workspace(
    name = "my_workspace",
    client=client
)

created_workspace = workspace_to_create.create()
created_workspace
```
!!! tip "Accessing attributes"
    Access the attributes of a workspace by calling them directly on the `Workspace` object. For example, `workspace.id` or `workspace.name`.

## List workspaces

You can list all the existing workspaces in Argilla by calling the `workspaces` attribute on the `Argilla` class and iterating over them. You can also use `len(client.workspaces)` to get the number of workspaces.

```python
import argilla_sdk as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

workspaces = client.workspaces

for workspace in workspaces:
    print(workspace)
```
!!! tip "Notebooks"
    When using a notebook, executing `client.workspaces` will display a table with the number of `datasets` in each workspace, `name`, `id`, and the last update as `updated_at`.

## Retrieve a workspace

You can retrieve a workspace by accessing the `workspaces` method on the `Argilla` class and passing the name of the workspace as an argument.

```python
import argilla_sdk as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

retrieved_workspace = client.workspaces("my_workspace")
```

## Check workspace existence

You can check if a workspace exists by calling the `exists` method on the `Workspace` class. This method returns a boolean value.

```python
import argilla_sdk as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

workspace = client.workspaces("my_workspace")

workspace_existed = workspace.exists()
```

## List users in a workspace

You can list all the users in a workspace by accessing the `users` attribute on the `Workspace` class and iterating over them. You can also use `len(workspace.users)` to get the number of users by workspace.

> For further information on how to manage users, check this [how-to guide](user.md).

```python
import argilla_sdk as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

workspace = client.workspaces('my_workspace')

for user in workspace.users:
    print(user)
```

## Add a user to a workspace

You can also add a user to a workspace by calling the `add_user` method on the `Workspace` class.

> For further information on how to manage users, check this [how-to guide](user.md).

```python
import argilla_sdk as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

workspace = client.workspaces("my_workspace")

added_user = workspace.add_user("my_username")
```

## Remove a user from workspace

You can also remove a user from a workspace by calling the `remove_user` method on the `Workspace` class.

> For further information on how to manage users, check this [how-to guide](user.md).

```python
import argilla_sdk as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

workspace = client.workspaces("my_workspace")

removed_user = workspace.remove_user("my_username")
```

## Delete a workspace

To delete a workspace, **no dataset can be associated with it**. If the workspace contains any dataset, deletion will fail. You can delete a workspace by calling the `delete` method on the `Workspace` class.

> To clear a workspace and delete all their datasets, refer to this [how-to guide](dataset.md).

```python
import argilla_sdk as rg

client = rg.Argilla(api_url="<api_url>", api_key="<api_key>")

workspace_to_delete = client.workspaces("my_workspace")

deleted_workspace = workspace_to_delete.delete()
```