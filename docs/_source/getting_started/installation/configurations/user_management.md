# User Management

This guide explains how to setup the users and team workspaces for your Argilla instance.

Let's first describe Argilla's user management model:

## User management model

### `User`

An Argilla user is defined by the following fields:

- `username`: The username used as login for Argilla's Webapp.
- `first_name`: The user's first name
- `last_name` (optional): The user's last name
- `role`: The user's role in Argilla. Available roles are: "admin" and "annotator". Only "admin" users can create and delete workspaces and datasets
- `workspaces` : The workspaces where the user has read and write access (both from the Webapp and the Python client). If this field is not defined the user will be a super-user and have access to all datasets in the instance. If this field is set to an empty list `[]` the user will only have access to her user workspace. Read more about workspaces and users below.
- `api_key`: The API key to interact with Argilla API, mainly through the Python client but also via HTTP for advanced users.

### `Workspace`

A workspace is a "space" inside your Argilla instance where users can collaborate. It is accessible through the UI and the Python client:

- `Team workspace`: Where one or several users have read/write access.
- `User workspace`: Every user gets its own user workspace. This workspace is the default workspace when users log and load data with the Python client. The name of this workspace corresponds to the username.

A user is given access to a workspace by including the name of the workspace in the list of workspaces defined by the `workspaces` field. **Users with no defined workspaces field are super-users** and have access and right to all datasets.


### Python client

The Python client gives developers the ability to log, load, and copy datasets from and to different workspace. Check out the [Python Reference](../reference/python/python_client.rst) for the parameter and methods related to workspaces.
Some examples are:

```python
import argilla as rg

# After this init, all logging and loading will use the specified workspace
rg.init(workspace="my_shared_workspace")

# Setting the workspace explicitly will also affect all logging and loading
rg.set_workspace("my_private_workspace")
```

## Default user

By default, if the Argilla instance has no users, the following default admin user will be configured:

- username: `argilla`
- password: `1234`
- api_key: `argilla.apikey`

For security reasons, we recommend changing at least the password and the API key. You can configure
the default user as follows:

```bash
python -m argilla.tasks.users.create_default --password newpassword --api-key new-api-key
```


:::{note}
To connect to an old Argilla server using client `>=1.3.0`, you should specify the default user API key `rubrix.apikey`.
Otherwise, connections will fail with an Unauthorized server error.
:::

## Add new users and workspaces

The above user management model is configured using the Argilla tasks, which server maintainers can define before launching an Argilla instance.

### Prepare the database
First of all, you need to make sure that database tables and models are up-to-date. This task must be launched when a new version of Argilla is installed.

```bash
python -m argilla.tasks.database.migrate
```

:::{note}
It is important to launch this task prior to any other database action.
:::


### Creating an admin user
```bash
python -m argilla.tasks.users.create --role admin
```

### Creating an annotator user
```bash
python -m argilla.tasks.users.create --role annotator
```

### HOWTO Create a new workspace an assign it to an existing annotator

#### 1. Setup a http client with an admin auth header

```python
auth_headers = {"X-Argilla-API-Key": "argilla.apikey"}
http = httpx.Client(base_url="http://localhost:6900", headers=auth_headers)
```

#### 2. Call the create workspace endpoint

```python
workspace = http.post("/api/workspaces", json={"name": "new-workspace"}).json()
workspace
```

#### 3. Select which annotators will be linked to then new workspace and link them by using their ids
```python
users = http.get("/api/users").json()
workspace_id = workspace["id"]
for user in users:
	if user["role"] == "annotator": # All annotators will be linked to the new workspace
		user_id = user["id"]
		response = http.post(f"/api/workspaces/{workspace_id}/users/{user_id}")
		print(response.json())
```


### HOWTO migrate users from the `users.yaml` file

```bash
export ARGILLA_LOCAL_AUTH_USERS_DB_FILE=/path/to/.users.yaml
python -m argilla.tasks.users.migrate
```

#### Migrate users with docker-compose

Make sure you create the yaml file above in the same folder as your `docker-compose.yaml`. You can download the `docker-compose` from this [URL](https://raw.githubusercontent.com/argilla-io/argilla/main/docker-compose.yaml):

Then open the provided ``docker-compose.yaml`` and configure your Argilla instance as follows:

{{ dockercomposeuseryaml }}

Then, you can run the migrate tasks as follows:

```bash
docker-compose exec argilla python -m argilla.tasks.users.migrate
```

If everything went well, the configured users can now log in, their annotations will be tracked with their usernames, and they'll have access to the defined workspaces.