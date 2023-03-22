# Docker Quickstart

Argilla is composed of a Python Server with Elasticsearch as the database layer, and a Python Client to create and
manage datasets.

To get started you just need to run the docker image with following command:

``` bash
  docker run -d --network argilla-net --name quickstart -p 6900:6900 argilla/argilla-quickstart:latest
```

<div class="alert alert-warning">

Apple Silicon Issues

Apple Silicon M1/M2 users might have issues with this deployment. To resolve this, use the `--platform linux/arm64` parameter. If this doesn't work, deploying separate images or via docker-compose will work.

</div>

This will run the latest quickstart docker image with 2 users `admin` and `argilla`. The password for these users is `12345678`. You can also configure these [environment variables](#environment-variables) as per your needs.

## Environment Variables

- `ADMIN_USERNAME`: The admin username to log in Argilla. The default admin username is `admin`. By setting up
  a custom username you can use your own username to log in to the app.
- `ADMIN_API_KEY`: Argilla provides a Python library to interact with the app (read, write, and update data, log model
  predictions, etc.). If you don't set this variable, the library and your app will use the default API key
  i.e. `admin.apikey`. If you want to secure your app for reading and writing data, we recommend you to set up this
  variable. The API key you choose can be any string of your choice and you can check an online generator if you like.
- `ADMIN_PASSWORD`: This sets a custom password to log in to the app with the `argilla` username. The default
  password is `12345678`. By setting up a custom password you can use your own password to login into the app.
- `ANNOTATOR_USERNAME`: The annotator username to login in Argilla. The default annotator username is `argilla`. By setting up
  a custom username you can use your own username to login into the app.
- `ANNOTATOR_PASSWORD`: This sets a custom password for login into the app with the `argilla` username. The default password
  is `12345678`. By setting up a custom password you can use your own password to login into the app.
- `LOAD_DATASETS`: This variables will allow you to load sample datasets. The default value will be `full`. The
  supported values for this variable is as follows:
    1. `single`: Load single datasets for TextClassification task.
    2. `full`: Load all the sample datasets for NLP tasks (TokenClassification, TextClassification, Text2Text)
    3. `none`: No datasets are loaded.
