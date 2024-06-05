# Workspace and Dataset Management

This guide explains how to set up and manage the workspaces in Argilla via the Python client.

:::{note}
The `Workspace` class for workspace management has been included as of the Argilla 1.11.0 release and is not available in previous versions. But you will be able to use it with older Argilla instances, from 1.6.0 onwards, the only difference will be that the main role is now `owner` instead of `admin`.
:::

## Workspace Model

A workspace is a "space" inside your Argilla instance where authorized users can collaborate. It is accessible through the UI and the Python client.

If you're an owner, you can assign users to workspaces, either when you create a new user, or using the method `add_user` from the `Workspace` class.

An `owner` has full access to the workspace, and can assign other users to it while the `admin` role can only access the workspace but cannot assign other users to it, and the `annotator` role can only access their assigned datasets in the workspace they belong to and annotate it via the UI.

An Argilla workspace is composed of the following attributes:

| Attribute | Type | Description |
| --- | --- | --- |
| `id` | `UUID` | The unique identifier of the workspace. |
| `name` | `str` | The name of the workspace. |
| `inserted_at` | `datetime` | The date and time when the workspace was created. |
| `updated_at` | `datetime` | The date and time when the workspace was last updated. |

### Python client

The `Workspace` class in the Python client gives developers with `owner` role the ability to create and manage workspaces in Argilla, and the users that belong to them. Check the [Workspace - Python Reference](/reference/python/python_workspaces.rst) to see the attributes, arguments, and methods of the `Workspace` class.

The `Workspace` class in Argilla is composed of the following attributes:

| Attribute | Type | Description |
| --- | --- | --- |
| `id` | `UUID` | The unique identifier of the workspace. |
| `name` | `str` | The name of the workspace. |
| `users` | `List[User]` | The list of users that belong to the workspace. |
| `inserted_at` | `datetime` | The date and time when the workspace was created. |
| `updated_at` | `datetime` | The date and time when the workspace was last updated. |

## How to work with Workspaces

### Create a new `Workspace`

::::{tab-set}

:::{tab-item} CLI
You can create a new workspace in Argilla using the `create` command in the `workspaces` group.

```bash
argilla workspaces create my-new-workspace
```
:::

:::{tab-item} Python client

Creating a workspace in Argilla is now as easy as calling the `create` method from the `Workspace` class. It will return a `Workspace` instance.

```python
import argilla as rg

rg.init(api_url="<ARGILLA_API_URL>", api_key="<ARGILLA_API_KEY>")

workspace = rg.Workspace.create("new-workspace")
```
:::

::::

### List `Workspaces`

The users with `owner` role can list all the existing workspaces in Argilla, while the users with `admin` role or `annotator` role can only list the workspaces they belong to.

::::{tab-set}

:::{tab-item} CLI
You can list the workspaces in Argilla using the `list` command in the `workspaces` group.

```bash
argilla workspaces list
```
:::

:::{tab-item} Python client
You can also list the workspaces in Argilla using the `list` method. It will return a list of `Workspace` instances.

```python
import argilla as rg

rg.init(api_url="<ARGILLA_API_URL>", api_key="<ARGILLA_API_KEY>")

workspaces = rg.Workspace.list()
for workspace in workspaces:
   ...
```
:::

::::

### Get a `Workspace` by name

#### Python client

You can get a workspace by its name using the `from_name` method. It must exist in advance in Argilla, otherwise, an exception will be raised.

```python
import argilla as rg

rg.init(api_url="<ARGILLA_API_URL>", api_key="<ARGILLA_API_KEY>")

workspace = rg.Workspace.from_name("new-workspace")
```

### Get a `Workspace` by id

#### Python client

Additionally, if you know the `id` of the workspace, you can get it directly using the `from_id` method. It must exist in advance in Argilla, otherwise, an exception will be raised.

:::{note}
The `id` of a workspace is a UUID, and it is generated automatically when you create a new workspace.
:::

```python
import argilla as rg

rg.init(api_url="<ARGILLA_API_URL>", api_key="<ARGILLA_API_KEY>")

workspace = rg.Workspace.from_id("00000000-0000-0000-0000-000000000000")
```

### Add, list, or delete users from a `Workspace`

::::{tab-set}

:::{tab-item} CLI

You can add or delete users from a workspace using the `add-user` and `delete-user` commands in the `workspaces` group.

```bash
argilla workspaces --name my-workspace add-user bob
argilla workspaces --name my-workspace delete-user bob
```

Also, you can list the users of a workspace using the `list` command in the `users` group with the `--workspace` option.

```bash
argilla users list --workspace my-workspace
```

:::

:::{tab-item} Python client

Once you instantiate a `Workspace` instance from a workspace in Argilla, you can add, list, or delete users from it. But note that just the `owner` has sufficient permissions to perform those operations.

```python
import argilla as rg

rg.init(api_url="<ARGILLA_API_URL>", api_key="<ARGILLA_API_KEY>")

workspace = rg.Workspace.from_name("new-workspace")

users = workspace.users
for user in users:
   ...
workspace.add_user(user.id)
workspace.delete_user(user.id)
```
:::

::::

### Delete a `Workspace`

#### Python client

You can also delete a workspace using the Python client.

:::{note}
To delete a workspace, no dataset can be linked to it. If the workspace contains any dataset, deletion will fail.
:::
:::{note}
You can refer to the [delete datasets](#delete-datasets) section below to clear a workspace before deleting it.
:::

```python
import argilla as rg

rg.init(api_url="<ARGILLA_API_URL>", api_key="<ARGILLA_API_KEY>")

workspace = rg.Workspace.from_name("new-workspace")

workspace.delete()
```
## Dataset Model

A dataset is a container of the "records" of your Argilla instance. It offers all the requirements for storing and managing the data. You can find more information about the concepts and structures of datasets [here](conceptual_guides/data_model.md#dataset).

On the Argilla UI, you can see all the datasets you have created. A dataset is created within a workspace and it is only reachable via this specific workspace. Depending on the project, as you give access to `owner`, `admin` or `annotator`, you also specify which roles can reach each dataset.

The attributes of a dataset are as follows:

| Attribute | Type | Description |
| --- | --- | --- |
| `id` | `UUID` | The unique identifier of the dataset. |
| `name` | `str` | The name of the dataset. |
| `url` | `str` | The unique URL of the dataset. |
| `fields` | `list` | The TextFields that the dataset contains. |
| `questions` | `list` | The questions that the dataset contains. |
| `guidelines` | `str` | The guidelines that the dataset has. |


## How to work with Datasets

You can refer to the [CLI page](/reference/cli.md) for guidance on how to work with datasets on CLI.

:::{note}
To work with the datasets on Python, you need to log in to Argilla with `rg.init()`.
:::

### List `Datasets`

#### Python client

You can list the datasets within a specific workspace with the `list()` method as seen below. To specify the workspace, you can use the `workspace` argument. Otherwise, it will list all the datasets in all workspaces.

```python
import argilla as rg

rg.init(api_url="<ARGILLA_API_URL>", api_key="<ARGILLA_API_KEY>")

dataset_list = rg.FeedbackDataset.list(workspace="admin")

for dataset in dataset_list:
   print(dataset.name)
```

As the `list()` method creates a list of `RemoteFeedbackDataset` objects, you can directly work each item of the list.

### Delete `Datasets`

#### Python client

You can delete any dataset by pulling it from the server by `from_argilla()` and calling the `delete()` method.

```python
rg.FeedbackDataset.from_argilla("my_dataset", workspace="admin").delete()
```
