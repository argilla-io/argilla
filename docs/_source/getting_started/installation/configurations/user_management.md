# User Management

This guide explains how to setup and manage the users in Argilla via the Python client and the CLI.

:::{note}
The `User` class for user management has been included as of the Argilla 1.11.0 release, and is not available in previous versions. But you will be able to use it with older Argilla instances, from 1.6.0 onwards, the only difference will be that the main role is now `owner` instead of `admin`.
:::

:::{warning}
As of Argilla 1.11.0 the default pool of users in the quickstart contains also an owner user which uses the credentials: username `owner`, password `12345678`, and API key `owner.apikey`; while for the server image the default user is now an `owner` instead of an `admin` with the same credentials: username `argilla`, password `1234` and API key `argilla.apikey`.
:::

## User Model

A user in Argilla is an authorized person who can access the UI and use the Python client and CLI in a running Argilla instance.

We differentiate between three types of users depending on their role:

- **Owner**: The owner is the user who created the Argilla instance. It has full access to all workspaces and can create new users and workspaces.
- **Admin**: An admin user can only access the workspaces it has been assigned to. Admin users can manage datasets on assigned workspaces.
- **Annotator**: As admin users, an annotator user can only access the workspaces it has been assigned to.

An Argilla user composed of the following attributes:

| Attribute | Type | Description |
| --- | --- | --- |
| `id` | `UUID` | The unique identifier of the user. |
| `username` | `str` | The username used as login for Argilla's UI. |
| `first_name` | `str` | The user's first name. |
| `last_name` | `str` | The user's last name. |
| `full_name` | `str` | The user's full name, which is the concatenation of `first_name` and `last_name`. |
| `role` | `str` | The user's role in Argilla. Available roles are: "owner", "admin" and "annotator". |
| `workspaces` | `List[str]` | The workspace names where the user has read and write access (both from the UI and the Python client). |
| `api_key` | `str` | The API key to interact with Argilla API, mainly through the Python client but also via HTTP for advanced users. It is automatically generated when a user is created. |
| `inserted_at` | `datetime` | The date and time when the user was created. |
| `updated_at` | `datetime` | The date and time when the user was last updated. |

### Python client

The `User` class in the Python client gives developers with `owner` role the ability to create and manage users in Argilla. Check the [User - Python Reference](../reference/python/python_users.rst) to see the attributes, arguments, and methods of the `User` class.

The above user management model is configured using the Argilla tasks, which server maintainers can define before launching an Argilla instance.

## Prepare the database

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

### Migrate DB to an specific version

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

## How to guide

:::{note}
To connect to an old Argilla instance (`<1.3.0`) using newer clients, you should specify the default user API key `rubrix.apikey`. Otherwise, connections will fail with an Unauthorized server error.
:::

### Get default `User`

#### CLI

By default, if the Argilla instance has no users, the following default owner user will be configured:

- username: `argilla`
- password: `12345678`
- api_key: `argilla.apikey`

For security reasons, we recommend changing at least the password and the API key. You can do this via the following CLI command:

```bash
python -m argilla users create_default --password new-password --api-key new-api-key
```

Which should produce the following output:

```bash
User with default credentials succesfully created:
• username: 'argilla'
• password: 'newpassword'
• api_key:  'new-api-key'
```

#### Python client

You can get the current active user in Argilla using the `me` classmethod in the `User` class. Note that the `me` method will return the active user as specified via the credentials provided via `rg.init`.

```python
import argilla as rg

rg.init(api_url="<ARGILLA_API_URL>", api_key="<ARGILLA_API_KEY>")

user = rg.User.me()
```

### Create a `User`

#### CLI

You can create a new user in Argilla using the `create` command in the `users` group.

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

  --role [owner|annotator]  Role for the user.  [default: annotator]
  --password TEXT           Password as a string with a minimum length of 8
                            characters.

  --api-key TEXT            API key as a string with a minimum length of 8
                            characters. If not specified a secure random API
                            key will be generated

  --workspace TEXT          A workspace that the user will be a member of (can
                            be used multiple times).

  --help                    Show this message and exit.
```

So for example, to create a new user with `admin` role, you can run the following command:

```bash
python -m argilla users create --username new-user --first-name New --last-name User --password new-password --role admin
```

#### Python client

You can also create a new user in Argilla using the `create` classmethod in the `User` class.

```python
import argilla as rg

rg.init(api_url="<ARGILLA_API_URL>", api_key="<ARGILLA_API_KEY>")

user = rg.User.create(
    username="new-user",
    first_name="New",
    last_name="User",
    password="new-password",
    role="admin",
)
```

### Update a `User`

#### CLI

You can change the assigned role for an existing user.

```bash
python -m argilla users update argilla --role owner
```
```bash
User 'argilla' successfully updated:
• role: 'admin' -> 'owner'
```

:::{note}
You should use this command to review and migrate user roles from version `<=1.10.0`
:::

### Get a `User` by username

#### Python client

You can get a user by username using the `from_name` classmethod in the `User` class.

```python
import argilla as rg

rg.init(api_url="<API_URL>", api_key="<OWNER_API_KEY>")

user = rg.User.from_name("new-user")
```

### Get a `User` by id

#### Python client

You can get a user by id using the `from_id` classmethod in the `User` class.

```python
import argilla as rg

rg.init(api_url="<ARGILLA_API_URL>", api_key="<ARGILLA_API_KEY>")

user = rg.User.from_id("new-user")
```

### Assign a `User` to a `Workspace`

#### CLI

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

#### Python client

To assign a user to a workspace, you can use the `add_user` method in the `Workspace` class. For more information about workspaces, see the [Workspace Management](./workspace_management.md) guide.

```python
import argilla as rg

rg.init(api_url="<API_URL>", api_key="<OWNER_API_KEY>")

user = rg.User.create(
    username="nick",
    first_name="Nick",
    last_name="Name",
    password="11223344",
    role="annotator",
)

workspace = rg.Workspace.create(name="ws")
workspace.add_user(user.id)
```

### List `User`s

#### Python client

You can list all the existing users in Argilla calling the `list` classmethod of the `User` class.

:::{note}
Just the "owner" can list all the users in Argilla.
:::

```python
import argilla as rg

rg.init(api_url="<API_URL>", api_key="<OWNER_API_KEY>")

users = rg.User.list()
```

### Delete a `User`

#### Python client

You can delete an existing user from Argilla calling the `delete` method on the `User` class.

:::{note}
Just the "owner" can delete users in Argilla.
:::

```python
import argilla as rg

rg.init(api_url="<ARGILLA_API_URL>", api_key="<ARGILLA_API_KEY>")

user = rg.User.from_name("existing-user")
user.delete()
```

### Migrate users from the `users.yaml` file

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

The user role will be computed depending on how workspaces are setup for each user. If no `workspace` attribute is defined, the user will be considered an `owner`. Otherwise, the assigned user role will be `annotator`.

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

Ensure everything went as expected via the `User` class from the Python client:

```python
import argilla as rg

rg.init(api_url="<ARGILLA_API_URL>", api_key="<ARGILLA_API_KEY>")

users = rg.User.list()
for user in users:
   print(f"username={user.username} role={user.role} workspaces={user.workspaces}")
```

Which should print:

```
username=john role=owner workspaces=['john']
username=tanya role=annotator workspaces=['tanya', 'argilla', 'team']
username=daisy role=annotator workspaces=['daisy', 'argilla', 'team', 'latam']
```

### Migrate users with Docker Compose

Make sure you create the YAML file above in the same folder as your `docker-compose.yaml`. You can download the `docker-compose.yaml` file from this [URL](https://raw.githubusercontent.com/argilla-io/argilla/main/docker/docker-compose.yaml):

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
