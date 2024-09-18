# Docker Quickstart

Argilla is composed of a Python Server with Elasticsearch as the database layer, and a Python Client to create and manage datasets, users, and workspaces.

To get started you just need to run the docker image with the following command:

``` bash
  docker run -d --network argilla-net --name quickstart -p 6900:6900 argilla/argilla-quickstart:latest
```

```{warning}

Apple Silicon M1/M2 users might have issues with this deployment. To resolve this, use the `--platform linux/arm64` parameter. If this doesn't work, deploying separate images or via docker-compose will work.

```

This will run the latest quickstart docker image with 3 users `owner`, `admin` and `argilla`. The password for these users is `12345678`. You can also configure these [environment variables](#environment-variables) as per your needs.

## Environment Variables

- `OWNER_USERNAME`: The owner username to log in Argilla. The default owner username is `owner`. By setting up
  a custom username you can use your own username to log in to the app.
- `OWNER_PASSWORD`: This sets a custom password to log in to the app with the `owner` username. The default
  password is `12345678`. By setting up a custom password you can use your own password to log in to the app.
- `OWNER_API_KEY`: Argilla provides a Python library to interact with the app (read, write, and update data, log model
  predictions, etc.). If you don't set this variable, the library and your app will use the default API key
  i.e. `owner.apikey`. If you want to secure your app for reading and writing data, we recommend you to set up this
  variable. The API key you choose can be any string of your choice and you can check an online generator if you like.
- `ADMIN_USERNAME`: The admin username to log in Argilla. The default admin username is `admin`. By setting up
  a custom username you can use your own username to log in to the app.
- `ADMIN_PASSWORD`: This sets a custom password to log in to the app with the `argilla` username. The default
  password is `12345678`. By setting up a custom password you can use your own password to log in to the app.
- `ADMIN_API_KEY`: Argilla provides a Python library to interact with the app (read, write, and update data, log model
  predictions, etc.). If you don't set this variable, the library and your app will use the default API key
  i.e. `admin.apikey`. If you want to secure your app for reading and writing data, we recommend you to set up this
  variable. The API key you choose can be any string of your choice and you can check an online generator if you like.
- `ANNOTATOR_USERNAME`: The annotator username to log in in Argilla. The default annotator username is `argilla`. By setting
  up a custom username you can use your own username to log in to the app.
- `ANNOTATOR_PASSWORD`: This sets a custom password to log in to the app with the `argilla` username. The default password
  is `12345678`. By setting up a custom password you can use your own password to log in to the app.
- `LOAD_DATASETS`: This variable will allow you to load sample datasets. The default value will be `full`. The
  supported values for this variable are as follows:
    1. `single`: Load single datasets for Feedback task.
    2. `full`: Load all the sample datasets for NLP tasks (Feedback, TokenClassification, TextClassification, Text2Text)
    3. `none`: No datasets are loaded.
- `REINDEX_DATASETS`: This variable will allow you to reindex the datasets. This must be done when a new version includes changes in the search index definition.
  The default value will be `false`. The supported values for this variable are as follows:
    1. `true`: Reindex the datasets.
    2. `false`: Do not reindex the datasets.