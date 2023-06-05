# User Management

This guide explains how to setup the users and team workspaces for your Argilla instance.

Let's first describe Argilla's user management model:

## User management model

### `User`

An Argilla user is defined by the following fields:

- `username`: The username used as login for Argilla's UI.
- `first_name`: The user's first name.
- `last_name` (optional): The user's last name.
- `role`: The user's role in Argilla. Available roles are: "admin" and "annotator". Only "admin" users can create and delete workspaces and datasets, and change the dataset settings, like the labeling schema.
- `workspaces`: The workspaces where the user has read and write access (both from the UI and the Python client). Read more about workspaces and users below.
- `api_key`: The API key to interact with Argilla API, mainly through the Python client but also via HTTP for advanced users. It is automatically generated when a user is created.

### `Workspace`

A workspace is a "space" inside your Argilla instance where authorized users can collaborate. It is accessible through the UI and the Python client.

You can assign users to workspaces when you create a new user, or by using the proper API endpoint. "Admin" users have access to ALL defined workspaces.

The Python client gives developers the ability to log, load, and copy datasets from and to different workspaces.

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
python -m argilla users create_default --password new-password --api-key new-api-key
```

```bash
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
python -m argilla database migrate
```

```
command: alembic -c /path/to/alembic.ini upgrade head
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 74694870197c, create users table
INFO  [alembic.runtime.migration] Running upgrade 74694870197c -> 82a5a88a3fa5, create workspaces table
INFO  [alembic.runtime.migration] Running upgrade 82a5a88a3fa5 -> 1769ee58fbb4, create workspaces_users table
```

:::{note}
It is important to launch this task prior to any other database action.
:::

#### Migrate to an specific version

If you want to apply migrations corresponding to a specific version or revision, for example, to apply a version rollback, you can pass the `--revision` option to the database migrate command:
```bash
python -m argilla database migrate --version 1.7
```

````bash
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
command: alembic -c /path/to/alembic.ini downgrade 1769ee58fbb4
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running downgrade ae5522b4c674 -> e402e9d9245e, create fields table
INFO  [alembic.runtime.migration] Running downgrade e402e9d9245e -> 8be56284dac0, create responses table
INFO  [alembic.runtime.migration] Running downgrade 8be56284dac0 -> 3a8e2f9b5dea, create records table
INFO  [alembic.runtime.migration] Running downgrade 3a8e2f9b5dea -> b9099dc08489, create questions table
INFO  [alembic.runtime.migration] Running downgrade b9099dc08489 -> 1769ee58fbb4, create datasets table
````

To see the available revisions you use the `database revisions` command:
```bash
python -m argilla database revisions
```

```bash
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.

Tagged revisions
-----------------
• 1.7 (revision: '1769ee58fbb4')
• 1.8 (revision: 'ae5522b4c674')

Alembic revisions
-----------------
e402e9d9245e -> ae5522b4c674 (head), create fields table
8be56284dac0 -> e402e9d9245e, create responses table
3a8e2f9b5dea -> 8be56284dac0, create records table
b9099dc08489 -> 3a8e2f9b5dea, create questions table
1769ee58fbb4 -> b9099dc08489, create datasets table
82a5a88a3fa5 -> 1769ee58fbb4, create workspaces_users table
74694870197c -> 82a5a88a3fa5, create workspaces table
<base> -> 74694870197c, create users table

Current revision
----------------
Current revision(s) for sqlite:////path/to/argilla.db?check_same_thread=False:
Rev: 1769ee58fbb4
Parent: 82a5a88a3fa5
Path: /path/to/alembic/versions/1769ee58fbb4_create_workspaces_users_table.py

    create workspaces_users table

    Revision ID: 1769ee58fbb4
    Revises: 82a5a88a3fa5
    Create Date: 2023-02-14 10:36:56.313539
```

### Creating users

```bash
python -m argilla users create
```

```
Usage: python -m argilla users create [OPTIONS]

  Creates a new user in the Argilla database with provided parameters

Options:
  --first-name TEXT
  --last-name TEXT
  --username TEXT           Username as a lowercase string without spaces
                            allowing letters, numbers, dashes and underscores.

  --role [admin|annotator]  Role for the user.  [default: annotator]
  --password TEXT           Password as a string with a minimum length of 8
                            characters.

  --api-key TEXT            API key as a string with a minimum length of 8
                            characters. If not specified a secure random API
                            key will be generated

  --workspace TEXT          A workspace that the user will be a member of (can
                            be used multiple times).

  --help                    Show this message and exit.
```

#### Creating an admin user

**CLI:**

```bash
python -m argilla users create --role admin --first-name Hulio --last-name Ramos --username hurra --password abcde123
```

```
User succesfully created:
• first_name: 'Hulio'
• last_name: 'Ramos'
• username: 'hurra'
• role: 'admin'
• api_key: 'eZDbiNZSZuTyLnVxtxUQ5K4M4WHmPBvIvnc3wofqT7ZPmS33FERjgNd9IECsAdC4qEaks4yVxjomkbDXcjfUoiuotA2-mrdcSZCVUDGGbQE'
• workspaces: []
```

**Python:**

```python
auth_headers = {"X-Argilla-API-Key": "argilla.apikey"}
http = httpx.Client(base_url="http://localhost:6900", headers=auth_headers)

response = http.post("/api/users", json={"role": "admin", "first_name": "Hulio", "last_name": "Ramos", "username": "hurra", "password": "abcde123"})
repsonse.json()
```
```json
{
   "id":"8e62808e-df44-4135-87bd-d022f1d9fcf0",
   "username":"hurra",
   "role":"admin",
   "full_name":"Hulio Ramos",
   "workspaces":[],
   "api_key":"67Ae7sRYpvu98MqMMkrPNtYx-pyjrRCiyieiwXsE7qP2npG8Eo_8cGpx4EZKJ_APt1FQ7qtX5jcnrUBLq7iW6N5KRhd32pBfHLFHHbnqIK4",
   "inserted_at":"2023-03-16T11:11:59.871532",
   "updated_at":"2023-03-16T11:11:59.871532"
}
```


#### Creating an annotator user assigned to a workspace

**CLI:**

```bash
python -m argilla users create --role annotator --first-name Nick --last-name Name --username nick --password 11223344 --workspace ws
```

```
User successfully created:
• first_name: 'Nick'
• last_name: 'Name'
• username: 'nick'
• role: 'annotator'
• api_key: 'SrX9T_4DAWK65Ztp4sADfB3g05t3bpwjwgfIwR3BP90uRg_LkWlsBXccAI9KTRbedxMNDdw15pM-9p56vPQhFv88d8e-M7PzVDZave92qPA'
• workspaces: ['ws']
```

The workspace `ws` is automatically created and assigned to the user.

**Python:**

```python
import httpx

api_key = <admin-api-key>
auth_headers = {"X-Argilla-API-Key": api_key}
http = httpx.Client(base_url="http://localhost:6900", headers=auth_headers)

# Create the user
user = http.post("/api/users", json={"role": "annotator", "first_name": "Nick", "last_name": "Name", "username": "nick", "password": "11223344"}).json()
```
```json
{
   "id":"75190fff-d4b9-4625-b7d3-4cfe3c659054",
   "username":"nick",
   "role":"annotator",
   "full_name":"Nick Name",
   "workspaces":[],
   "api_key":"SrX9T_4DAWK65Ztp4sADfB3g05t3bpwjwgfIwR3BP90uRg_LkWlsBXccAI9KTRbedxMNDdw15pM-9p56vPQhFv88d8e-M7PzVDZave92qPA",
   "inserted_at":"2023-03-16T11:17:35.462774",
   "updated_at":"2023-03-16T11:17:35.462774"
}
```
```python
# Create the workspace
workspace = http.post("/api/workspaces", json={"name": "ws"}).json()
```
```json
{
   "id":"1908bd1f-058b-4e01-82d1-3be7dfcc2a70",
   "name":"ws",
   "inserted_at":"2023-03-16T11:18:45.506912",
   "updated_at":"2023-03-16T11:18:45.506912"
}
```
```python
# Assign user to workspace
http.post(f"/api/workspaces/{workspace['id']}/users/{user['id']}")

```
```json
{
   "id":"75190fff-d4b9-4625-b7d3-4cfe3c659054",
   "username":"nick",
   "role":"annotator",
   "full_name":"Nick Name",
   "workspaces":["ws"],
   "api_key":"SrX9T_4DAWK65Ztp4sADfB3g05t3bpwjwgfIwR3BP90uRg_LkWlsBXccAI9KTRbedxMNDdw15pM-9p56vPQhFv88d8e-M7PzVDZave92qPA",
   "inserted_at":"2023-03-16T11:17:35.462774",
   "updated_at":"2023-03-16T11:17:35.462774"
}
```

## Listing Argilla users

````python
users = http.get("/api/users").json()
````
```json
[
   {
      "id":"8e62808e-df44-4135-87bd-d022f1d9fcf0",
      "username":"hurra",
      "role":"admin",
      "full_name":"Hulio Ramos",
      "workspaces":[

      ],
      "api_key":"67Ae7sRYpvu98MqMMkrPNtYx-pyjrRCiyieiwXsE7qP2npG8Eo_8cGpx4EZKJ_APt1FQ7qtX5jcnrUBLq7iW6N5KRhd32pBfHLFHHbnqIK4",
      "inserted_at":"2023-03-16T11:11:59.871532",
      "updated_at":"2023-03-16T11:11:59.871532"
   },
   {
      "id":"75190fff-d4b9-4625-b7d3-4cfe3c659054",
      "username":"nick",
      "role":"annotator",
      "full_name":"Nick Name",
      "workspaces":[
         "ws2"
      ],
      "api_key":"SrX9T_4DAWK65Ztp4sADfB3g05t3bpwjwgfIwR3BP90uRg_LkWlsBXccAI9KTRbedxMNDdw15pM-9p56vPQhFv88d8e-M7PzVDZave92qPA",
      "inserted_at":"2023-03-16T11:17:35.462774",
      "updated_at":"2023-03-16T11:17:35.462774"
   }
]
```

## Delete a user

```python
http.delete("/api/users/75190fff-d4b9-4625-b7d3-4cfe3c659054").json()
```
```json
{
   "id":"75190fff-d4b9-4625-b7d3-4cfe3c659054",
   "username":"nick2",
   "role":"annotator",
   "full_name":"Nick Name",
   "workspaces":[
      "ws2"
   ],
   "api_key":"SrX9T_4DAWK65Ztp4sADfB3g05t3bpwjwgfIwR3BP90uRg_LkWlsBXccAI9KTRbedxMNDdw15pM",
   "inserted_at":"2023-03-16T11:17:35.462774",
   "updated_at":"2023-03-16T11:17:35.462774"
}
```

## Migrate users from the `users.yaml` file

The migration tasks can create users and workspaces automatically from a yaml file with the following format:

```yaml
- username: john
  full_name: John Doe
  email: john@argilla.io
  api_key: a14427ea-9197-11ec-b909-0242ac120002
  hashed_password: $2y$05$xtl7iy3bpqchUwiQMjEHe.tY7OaIjDrg43W3TB4EHQ7izvdjvGtPS
  disabled: False

- username: tanya
  full_name: Tanya Franklin
  email: tanya@argilla.io
  api_key: 78a10b53-8db7-4ab5-9e9e-fbd4b7e76551
  hashed_password: $2y$05$aqNyXcXRXddNj5toZwT0HugHqKZypvqlBAkZviAGGbsAC8oTj/P5K
  workspaces: [argilla, team]
  disabled: True

- username: daisy
  full_name: Daisy Gonzalez
  email: daisy@argilla.io
  api_key: a8168929-8668-494c-b7a5-98cd35740d9b
  hashed_password: $2y$05$l83IhUs4ZDaxsgZ/P12FO.RFTi2wKQ2AxMK2vYtLx//yKramuCcZG
  workspaces: [argilla, team, latam]
  disabled: False
```

The user role will be computed depending on how workspaces are setup for each user. If no `workspace` attribute is defined, the user will be considered an `admin`. Otherwise, the assigned user role will be `annotator`.

The task will also create an extra workspace for each user named after their username.

```bash
export ARGILLA_LOCAL_AUTH_USERS_DB_FILE=/path/to/.users.yml
python -m argilla users migrate
```

```
Starting users migration process using file '.users.yml'
Migrating User with username 'john'
Migrating User with username 'tanya'
Migrating User with username 'daisy'
Users migration process successfully finished
```

```python
http.get("/api/users").json()
```

```json
[
   {
      "id":"8e4da958-1dba-44d9-82f3-ea2ec3beecdf",
      "username":"john",
      "role":"admin",
      "full_name":"John Doe None",
      "workspaces":[
         "john"
      ],
      "api_key":"a14427ea-9197-11ec-b909-0242ac120002",
      "inserted_at":"2023-03-16T11:31:12.979241",
      "updated_at":"2023-03-16T11:31:12.979241"
   },
   {
      "id":"0ed76afb-e9a5-409c-9716-ac7ae919afe8",
      "username":"tanya",
      "role":"annotator",
      "full_name":"Tanya Franklin None",
      "workspaces":[
         "tanya",
         "argilla",
         "team"
      ],
      "api_key":"78a10b53-8db7-4ab5-9e9e-fbd4b7e76551",
      "inserted_at":"2023-03-16T11:31:12.986146",
      "updated_at":"2023-03-16T11:31:12.986146"
   },
   {
      "id":"944e4f76-6cf9-4242-8568-41b2d683cd9f",
      "username":"daisy",
      "role":"annotator",
      "full_name":"Daisy Gonzalez None",
      "workspaces":[
         "daisy",
         "argilla",
         "team",
         "latam"
      ],
      "api_key":"a8168929-8668-494c-b7a5-98cd35740d9b",
      "inserted_at":"2023-03-16T11:31:12.990718",
      "updated_at":"2023-03-16T11:31:12.990718"
   }
]
```

```python
http.get("/api/workspaces").json()
```

```json
[
   {
      "id":"96169426-c27b-48b7-a386-8f58193f8d64",
      "name":"john",
      "inserted_at":"2023-03-16T11:31:12.981784",
      "updated_at":"2023-03-16T11:31:12.981784"
   },
   {
      "id":"adc51bfb-3940-4f3a-ad2a-46bad05ffe90",
      "name":"tanya",
      "inserted_at":"2023-03-16T11:31:12.986924",
      "updated_at":"2023-03-16T11:31:12.986924"
   },
   {
      "id":"5d2e5fc1-179e-4b6a-8bc0-3eba4e85bba3",
      "name":"argilla",
      "inserted_at":"2023-03-16T11:31:12.986941",
      "updated_at":"2023-03-16T11:31:12.986941"
   },
   {
      "id":"abb6f7ca-9585-4499-a23b-4433be8c5a60",
      "name":"team",
      "inserted_at":"2023-03-16T11:31:12.986953",
      "updated_at":"2023-03-16T11:31:12.986953"
   },
   {
      "id":"3a2acec8-fc61-4704-993b-a8606dacaaf3",
      "name":"daisy",
      "inserted_at":"2023-03-16T11:31:12.991027",
      "updated_at":"2023-03-16T11:31:12.991027"
   },
   {
      "id":"bd314fdf-5f20-487a-989a-b628f2e2bbd6",
      "name":"latam",
      "inserted_at":"2023-03-16T11:31:12.991047",
      "updated_at":"2023-03-16T11:31:12.991047"
   }
]
```

### Migrate users with Docker Compose

Make sure you create the YAML file above in the same folder as your `docker-compose.yaml`. You can download the `docker-compose.yaml` file from this [URL](https://raw.githubusercontent.com/argilla-io/argilla/main/docker-compose.yaml):

Then open the provided `docker-compose.yaml` file and modify your Argilla instance as follows:

```diff
  argilla:
    image: argilla/argilla-server:latest
    restart: unless-stopped
    ports:
      - "6900:6900"
    environment:
      ARGILLA_HOME_PATH: /var/lib/argilla
      ARGILLA_ELASTICSEARCH: http://elasticsearch:9200
+     ARGILLA_LOCAL_AUTH_USERS_DB_FILE: /var/lib/argilla-migrate/users.yaml
    networks:
      - argilla
    volumes:
      - argilladata:/var/lib/argilla
+     - ${PWD}/users.yaml:/var/lib/argilla-migrate/users.yaml
```

After that change you can start the containers with:

```bash
docker-compose up
```

And after running the containers you can run the task to migrate the users as follows:

```bash
docker-compose exec argilla python -m argilla users migrate
```

If everything went well, the configured users can now log in, their annotations will be tracked with their usernames, and they'll have access to the defined workspaces.
