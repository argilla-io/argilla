.. _users_management:

Default user credentials
========================

- username: `rubrix`
- password: `1234`
- api key: `rubrix.apikey` (configured automatically by client)


Override user api key
---------------------

````bash
export RUBRIX_LOCAL_AUTH_DEFAULT_APIKEY=new-apikey
````

Override user password
----------------------

You must set an already hashed password in environment var

Generate an user password:

````bash
htpasswd -nbB "" <passwd>
````

then, configure the environment variable

```bash
export RUBRIX_LOCAL_AUTH_DEFAULT_PASSWORD="<generateed_user_password>"
```

Create a user db file
---------------------

Create a new yaml file like following:

```yaml
#.users.yaml
# User are provided as a list
- username: user1
  hashed_password: # <generated-hashed-password>. See previous steps
  api_key: "ThisIsTheUserAPIKEY"
- username: user2
  hashed_password: # <generated-hashed-password>. See previous steps
  api_key: "ThisIsTheUserAPIKEY"
...
```

Then, save the file in some local path and configure environment variable with stored path
```bash
export RUBRIX_LOCAL_AUTH_USERS_DB_FILE=/path/to/.users.yaml
```

Launch rubrix instance:
```bash
python -m rubrix.server
```
This configuration will make enable your configured users for data annotation


Configure using docker-compose
==============================

Be sure your users db file is created in same folder that your `docker-compose.yaml`.

Then, open provided `docker-compose.yaml` and configuration to rubrix service:
````yaml
docker-compose.yaml
services:
  rubrix:
    image: recognai/rubrix:latest
    ports:
      - "6900:80"
    environment:
      ELASTICSEARCH: http://elasticsearch:9200
      RUBRIX_LOCAL_AUTH_USERS_DB_FILE: /config/.users.yaml

    volumes:
      # We mount the local file .users.yaml in remote container in path /config/.users.yaml
      - ${PWD}/.users.yaml:/config/.users.yaml
      
    ...
````
You can reload the rubrix service to refresh the container:

````bash
docker-compose up -d rubrix
````

If everything went well, configured users can now log in and their annotations will be tracked with their usernames.