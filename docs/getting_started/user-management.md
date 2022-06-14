# User Management and Workspaces

This guide explains how to setup the users and team workspaces for your Rubrix instance.

Let's first describe Rubrix's user management model:

## User management model

### `User`

A Rubrix user is defined by the following fields:

- `username`: The username to use for login into the Webapp.
- `email`(optional): The user's email.
- `fullname` (optional): The user's full name
- `disabled`(optional): Whether this use is enabled (and can interact with Rubrix), this might be useful for disabling user access temporarily.
- `workspaces`(optional): The team workspaces where the user has read and write access (both from the Webapp and the Python client). If this field is not defined the user will be a super-user and have access to all datasets in the instance. If this field is set to an empty list `[]` the user will only have access to her user workspace. Read more about workspaces and users below.
- `api_key`: The API key to interact with Rubrix API, mainly through the Python client but also via HTTP for advanced users.

### `Workspace`

A workspace is a Rubrix "space" where users can collaborate, both using the Webapp and the Python client. There are two types of workspace:

- `Team workspace`: Where one or several users have read/write access.
- `User workspace`: Every user gets its own user workspace. This workspace is the default workspace when users log and load data with the Python client. The name of this workspace corresponds to the username.

A user is given access to a workspace by including the name of the workspace in the list of workspaces defined by the `workspaces` field. **Users with no defined workspaces field are super-users** and have access and right to all datasets.


### Python client methods and workspaces

The Python client gives developers the ability to log, load, and copy datasets from and to different workspace. Check out the [Python Reference](../reference/python/python_client.rst) for the parameter and methods related to workspaces.
Some examples are:

```python
import rubrix as rb

# After this init, all logging and loading will use the specified workspace
rb.init(workspace="my_shared_workspace")

# Setting the workspace explicitly will also affect all logging and loading
rb.set_workspace("my_private_workspace")
```

### *users.yml*

The above user management model is configured using a YAML file which server maintainers can define before launching a Rubrix instance.
This can be done when launching Rubrix from Python or with the provided `docker-compose.yml`. Read below for more details on the different options.

## Default user

By default, if you don't configure a `users.yml` file, your Rubrix instance is pre-configured with the following default user:

- username: `rubrix`
- password: `1234`
- api_key: `rubrix.apikey`

for security reasons we recommend changing at least the password and API key.

### How to override the default API key

To override the default API key you can set the following environment variable before launching the server:

```bash
export RUBRIX_LOCAL_AUTH_DEFAULT_APIKEY=new-apikey
```


### How to override the default user password

To override the password, you must set an environment variable that contains an already hashed password.
You can use `htpasswd` to generate a hashed password:

```bash
htpasswd -nbB "" my-new-password
:$apr1$n0C4S20a$noG.3yWxH1OIKfFITgzl30
```

Afterwards, set the environment variable omitting the first `:` character (in our case `$apr1$n0C4...`):

```bash
export RUBRIX_LOCAL_AUTH_DEFAULT_PASSWORD="<generated_user_password>"
```

Alternatively, you can also generate the hash using passlib's CryptContext: E.g., by running the following in a python console:

```python
from passlib.context import CryptContext
print(CryptContext(schemes=["bcrypt"], deprecated="auto").hash('password'))
```

## How to add new users and workspaces

To configure your Rubrix instance for various users, you just need to create a yaml file as follows:
```yaml
#.users.yaml
# Users are provided as a list
- username: user1
  hashed_password: <generated-hashed-password> # See the previous section above
  api_key: "ThisIsTheUser1APIKEY"
  workspaces: [] # This user will only have her user workspace available
- username: user2
  hashed_password: <generated-hashed-password> # See the previous section above
  api_key: "ThisIsTheUser2APIKEY"
  workspaces: ['client_projects'] # access to her user workspace and the client_projects workspace
- username: user3
  hashed_password: <generated-hashed-password> # See the previous section above
  api_key: "ThisIsTheUser2APIKEY" # this user can access all workspaces (including
- ...
```

Then point the following environment variable to this yaml file before launching the server:

```bash
export RUBRIX_LOCAL_AUTH_USERS_DB_FILE=/path/to/.users.yaml
```

If everything went well, the configured users can now log in and their annotations will be tracked with their usernames.


### Using docker-compose

Make sure you create the yaml file above in the same folder as your `docker-compose.yaml`. You can download the `docker-compose` from this [URL](https://git.io/rb-docker):

Then open the provided ``docker-compose.yaml`` and configure your Rubrix instance as follows:

{{ '```yaml\n{}\n```'.format(dockercomposeuseryaml) }}

You can reload the *Rubrix* service to refresh the container:

```bash
docker-compose up -d rubrix
```

If everything went well, the configured users can now log in, their annotations will be tracked with their usernames, and they'll have access to the defined workspaces.