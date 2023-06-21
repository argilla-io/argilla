# Workspace Management

This guide explains how setup and manage the workspaces in Argilla via the Python client.

:::{note}
The `Workspace` class for workspace management has been included as of the Argilla 1.11.0 release, and is not available in previous versions. But you will be able to use it with older Argilla instances, from 1.6.0 onwards, the only difference will be that the main role is now `owner` instead of `admin`.
:::

## Workspace Model

A workspace is a "space" inside your Argilla instance where authorized users can collaborate. It is accessible through the UI and the Python client.

If you're an owner, you can assign users to workspaces, either when you create a new user, or using the method `add_user` from the `Workspace` class.

An `owner` has full access to the workspace, and can assign other users to it; while the `admin` role can only access the workspace, but cannot assign other users to it; and the `annotator` role can only access their assigned datasets in the workspace they belong to and annotate it via the UI.

An Argilla workspace is composed of the following attributes:

| Attribute | Type | Description |
| --- | --- | --- |
| `id` | `UUID` | The unique identifier of the workspace. |
| `name` | `str` | The name of the workspace. |
| `inserted_at` | `datetime` | The date and time when the workspace was created. |
| `updated_at` | `datetime` | The date and time when the workspace was last updated. |

### Python client

The `Workspace` class in the Python client gives developers with `owner` role the ability to create and manage workspaces in Argilla, and the users that belong to them. Check the [Workspace - Python Reference](../reference/python/python_workspaces.rst) to see the attributes, arguments, and methods of the `Workspace` class.

The `Workspace` class in Argilla is composed of the following attributes:

| Attribute | Type | Description |
| --- | --- | --- |
| `id` | `UUID` | The unique identifier of the workspace. |
| `name` | `str` | The name of the workspace. |
| `users` | `List[User]` | The list of users that belong to the workspace. |
| `inserted_at` | `datetime` | The date and time when the workspace was created. |
| `updated_at` | `datetime` | The date and time when the workspace was last updated. |


## How to guide

### Create a new `Workspace`

#### Python client

Creating a workspace in Argilla is now as easy as calling the `create` method from the `Workspace` class. It will return a `Workspace` instance.

```python
import argilla as rg

rg.init(api_url="<ARGILLA_API_URL>", api_key="<ARGILLA_API_KEY>")

workspace = rg.Workspace.create("new-workspace")
```

### List all the existing `Workspaces`

#### Python client

You can also list all the existing workspaces in Argilla using the `list` method. It will return a list of `Workspace` instances.

```python
import argilla as rg

rg.init(api_url="<ARGILLA_API_URL>", api_key="<ARGILLA_API_KEY>")

workspaces = rg.Workspace.list()
for workspace in workspaces:
   ...
```

### Get a `Workspace` by name

#### Python client

You can get a workspace by its name using the `from_name` method. It must exist in advance in Argilla, otherwise an exception will be raised.

```python
import argilla as rg

rg.init(api_url="<ARGILLA_API_URL>", api_key="<ARGILLA_API_KEY>")

workspace = rg.Workspace.from_name("new-workspace")
```

### Get a `Workspace` by id

#### Python client

Additionally, if you know the `id` of the workspace, you can get it directly using the `from_id` method. It must exist in advance in Argilla, otherwise an exception will be raised.

:::{note}
The `id` of a workspace is a UUID, and it is generated automatically when you create a new workspace.
:::

```python
import argilla as rg

rg.init(api_url="<ARGILLA_API_URL>", api_key="<ARGILLA_API_KEY>")

workspace = rg.Workspace.from_id("00000000-0000-0000-0000-000000000000")
```

### Add, list, or delete users from a `Workspace`

#### Python client

Once you instantiate a `Workspace` instance from a workspace in Argilla, you can add, list, or delete users from it. But note that just the `owner` has sufficient permissions to perform those operations.

:::{note}
As of the 1.11.0 version of the Python client, to add and delete users from a `Workspace` one must use the `UUID` which is the unique identifier in Argilla for each user. To do so, one can simply use the `id` attribute of the `User` class. More information about it can be found in the [User - Python Reference](../reference/python/python_users.rst) or in the [User Management](user_management.md) guide.
:::

```python
import argilla as rg

rg.init(api_url="<ARGILLA_API_URL>", api_key="<ARGILLA_API_KEY>")

workspace = rg.Workspace.from_name("new-workspace")

users = workspace.users
for user in users:
   ...
workspace.add_user("<USER_ID>")
workspace.delete_user("<USER_ID>")
```
