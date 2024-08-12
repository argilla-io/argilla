---
hide: footer
---
# `rg.Argilla`

To interact with the Argilla server from Python you can use the `Argilla` class. The `Argilla` client is used to create, get, update, and delete all Argilla resources, such as workspaces, users, datasets, and records.

## Usage Examples

### Connecting to an Argilla server

To connect to an Argilla server, instantiate the `Argilla` class and pass the `api_url` of the server and the `api_key` to authenticate.

```python
import argilla as rg

client = rg.Argilla(
    api_url="https://argilla.example.com",
    api_key="my_api_key",
)
```

### Accessing Dataset, Workspace, and User objects

The `Argilla` clients provides access to the `Dataset`, `Workspace`, and `User` objects of the Argilla server.

```python

my_dataset = client.datasets("my_dataset")

my_workspace = client.workspaces("my_workspace")

my_user = client.users("my_user")

```

These resources can then be interacted with to access their properties and methods. For example, to list all datasets in a workspace:

```python
for dataset in my_workspace.datasets:
    print(dataset.name)
```


---

::: src.argilla.client.Argilla
