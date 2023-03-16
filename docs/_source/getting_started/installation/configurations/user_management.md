# User Management

This guide explains how to setup the users and team workspaces for your Argilla instance.

Let's first describe Argilla's user management model:

## User management model

### `User`

An Argilla user is defined by the following fields:

- `username`: The username used as login for Argilla's Webapp.
- `first_name`: The user's first name.
- `last_name` (optional): The user's last name.
- `role`: The user's role in Argilla. Available roles are: "admin" and "annotator". Only "admin" users can create and delete workspaces and datasets, and change the dataset settings, like the labeling schema.
- `workspaces`: The workspaces where the user has read and write access (both from the UI and the Python client). Read more about workspaces and users below.
- `api_key`: The API key to interact with Argilla API, mainly through the Python client but also via HTTP for advanced users. It is automatically generated when a user is created.

### `Workspace`

A workspace is a "space" inside your Argilla instance where authorized users can collaborate. It is accessible through the UI and the Python client.

You can assign users to workspaces when you create a new user, or by using the proper API endpoint. "Admin" users can access to ALL defined workspaces


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

For security reasons, we recommend changing at least the password and the API key. You can do this via the following CLI command:
```bash
&>python -m argilla.tasks.users.create_default --password newpassword --api-key new-api-key
User with default credentials succesfully created:
• username: 'argilla'
• password: 'newpassword'
• api_key:  'new-api-key'
```

:::{note}
To connect to an old Argilla instance (`<1.3.0`) using newer clients, you should specify the default user API key `rubrix.apikey`.
Otherwise, connections will fail with an Unauthorized server error.
:::

## Add new users and workspaces

The above user management model is configured using the Argilla tasks, which server maintainers can define before launching an Argilla instance.

### Prepare the database
First of all, you need to make sure that database tables and models are up-to-date. This task must be launched when a new version of Argilla is installed.

```bash
&>python -m argilla.tasks.database.migrate
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 74694870197c, create users table
INFO  [alembic.runtime.migration] Running upgrade 74694870197c -> 82a5a88a3fa5, create workspaces table
INFO  [alembic.runtime.migration] Running upgrade 82a5a88a3fa5 -> 1769ee58fbb4, create workspaces_users table
```

:::{note}
It is important to launch this task prior to any other database action.
:::


### Creating an admin user
**CLI:**
```bash
python -m argilla.tasks.users.create --role admin --first-name Hulio --last-name Ramos --username hurra --password abcde123
```

**Python:**
```python
auth_headers = {"X-Argilla-API-Key": "argilla.apikey"}
http = httpx.Client(base_url="http://localhost:6900", headers=auth_headers)

response = http.post("/api/users", json={"role": "admin", "first_name": "Hulio", "last_name": "Ramos", "username": "Hulio", "password": "abcde123"})
repsonse.json()
>>> {"id": "3ccc8776-8d91-4a72-90e6-e587b91b4cb9", "role: "admin", "first_name": "Hulio", "last_name": "Ramos", "username": "Hulio", "password": "abcde123"}
```

### Creating an annotator user
**CLI:**
```bash
python -m argilla.tasks.users.create --role annotator --first-name Hulio --last-name Ramos --username hurra --password abcde123
```

**Python:**
```python
auth_headers = {"X-Argilla-API-Key": "argilla.apikey"}
http = httpx.Client(base_url="http://localhost:6900", headers=auth_headers)

response = http.post("/api/users", json={"role": "annotator", "first_name": "Hulio", "last_name": "Ramos", "username": "Hulio", "password": "abcde123"})
repsonse.json()
>>> {"id": "69a0d5d1-c6eb-4f4e-9685-cfa20da7de5f", "role": "annotator", "first_name": "Hulio", "last_name": "Ramos", "username": "Hulio", "password": "abcde123"}
```

### Delete an user
```python
auth_headers = {"X-Argilla-API-Key": "argilla.apikey"}
http = httpx.Client(base_url="http://localhost:6900", headers=auth_headers)

# Getting users
users = http.get("/api/users").json()
>>> [
>>>   {"id": "69a0d5d1-c6eb-4f4e-9685-cfa20da7de5f", "role": "annotator", "first_name": "Hulio", "last_name": "Ramos", "username": "Hulio", "password": "abcde123"}, 
>>>   {"id": "3ccc8776-8d91-4a72-90e6-e587b91b4cb9", "role: "admin", "first_name": "Hulio", "last_name": "Ramos", "username": "Hulio", "password": "abcde123"}
>>> ]

response = http.delete(f"/api/users/69a0d5d1-c6eb-4f4e-9685-cfa20da7de5f")
repsonse.json()
>>> {"id": "69a0d5d1-c6eb-4f4e-9685-cfa20da7de5f", "role": "annotator", "first_name": "Hulio", "last_name": "Ramos", "username": "Hulio", "password": "abcde123"}

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
>>> { "id": "cc88ec50-f61d-4646-809e-7a03c8835df5", "name": "new-workspace"}
```

#### 3. Assign users to new workspace
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
