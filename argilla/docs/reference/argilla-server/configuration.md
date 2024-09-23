# Server configuration

This section explains advanced operations and settings for running the Argilla Server and Argilla Python Client.

By default, the Argilla Server will look for your Elasticsearch (ES) endpoint at `http://localhost:9200`. You can customize this by setting the `ARGILLA_ELASTICSEARCH` environment variable. Have a look at the list of available [environment variables](#environment-variables) to further configure the Argilla server.

From the Argilla version `1.19.0`, you must set up the search engine manually to work with datasets. You should set the
environment variable `ARGILLA_SEARCH_ENGINE=opensearch` or `ARGILLA_SEARCH_ENGINE=elasticsearch` depending on the backend you're using
The default value for this variable is set to `elasticsearch`. The minimal version for Elasticsearch is `8.5.0`, and for Opensearch is `2.4.0`.
Please, review your backend and upgrade it if necessary.

!!! warning
    For vector search in OpenSearch, the filtering applied is using a `post_filter` step, since there is a bug that makes queries fail using filtering + knn from Argilla.
    See https://github.com/opensearch-project/k-NN/issues/1286

    This may result in unexpected results when combining filtering with vector search with this engine.

## Launching

### Using a proxy

If you run Argilla behind a proxy by adding some extra prefix to expose the service, you should set the `ARGILLA_BASE_URL`
environment variable to properly route requests to the server application.

For example, if your proxy exposes Argilla in the URL `https://my-proxy/custom-path-for-argilla`, you should launch the
Argilla server with `ARGILLA_BASE_URL=/custom-path-for-argilla`.

NGINX and Traefik have been tested and are known to work with Argilla:

- [NGINX example](https://github.com/argilla-io/argilla/tree/main/examples/deployments/docker/nginx)
- [Traefik example](https://github.com/argilla-io/argilla/tree/main/examples/deployments/docker/traefik)

## Environment variables

You can set the following environment variables to further configure your server and client.

### Server

#### FastAPI

- `ARGILLA_HOME_PATH`: The directory where Argilla will store all the files needed to run. If the path doesn't exist it will be automatically created (Default: `~/.argilla`).

- `ARGILLA_BASE_URL`: If you want to launch the Argilla server in a specific base path other than /, you should set up this environment variable. This can be useful when running Argilla behind a proxy that adds a prefix path to route the service (Default: "/").

- `ARGILLA_CORS_ORIGINS`: List of host patterns for CORS origin access.

- `ARGILLA_DOCS_ENABLED`: If False, disables openapi docs endpoint at _/api/docs_.

- `HF_HUB_DISABLE_TELEMETRY`: If True, disables telemetry for usage metrics. Alternatively, you can disable telemetry by setting `HF_HUB_OFFLINE=1`.

#### Authentication

- `ARGILLA_AUTH_SECRET_KEY`: The secret key used to sign the API token data. You can use `openssl rand -hex 32` to generate a 32 character string to use with this environment variable. By default a random value is generated, so if you are using more than one server worker (or more than one Argilla server) you will need to set the same value for all of them.
- `USERNAME`: If provided, the owner username (Default: `""`).
- `PASSWORD`: If provided, the owner password.
If `USERNAME` and `PASSWORD` are provided, the owner user will be created with these credentials on the server startup (Default: `""`).


#### Database

- `ARGILLA_DATABASE_URL`: A URL string that contains the necessary information to connect to a database. Argilla uses SQLite by default, PostgreSQL is also officially supported (Default: `sqlite:///$ARGILLA_HOME_PATH/argilla.db?check_same_thread=False`).

##### SQLite

The following environment variables are useful only when SQLite is used:

- `ARGILLA_DATABASE_SQLITE_TIMEOUT`: How many seconds the connection should wait before raising an `OperationalError` when a table is locked. If another connection opens a transaction to modify a table, that table will be locked until the transaction is committed. (Defaut: `15` seconds).

##### PostgreSQL

The following environment variables are useful only when PostgreSQL is used:

- `ARGILLA_DATABASE_POSTGRESQL_POOL_SIZE`: The number of connections to keep open inside the database connection pool (Default: `15`).

- `ARGILLA_DATABASE_POSTGRESQL_MAX_OVERFLOW`: The number of connections that can be opened above and beyond `ARGILLA_DATABASE_POSTGRESQL_POOL_SIZE` setting (Default: `10`).

#### Search engine

- `ARGILLA_ELASTICSEARCH`: URL of the connection endpoint of the Elasticsearch instance (Default: `http://localhost:9200`).

- `ARGILLA_SEARCH_ENGINE`: Search engine to use. Valid values are "elasticsearch" and "opensearch" (Default: "elasticsearch").

- `ARGILLA_ELASTICSEARCH_SSL_VERIFY`: If "False", disables SSL certificate verification when connecting to the Elasticsearch backend.

- `ARGILLA_ELASTICSEARCH_CA_PATH`: Path to CA cert for ES host. For example: `/full/path/to/root-ca.pem` (Optional)

### Redis

Redis is used by Argilla to store information about jobs to be processed on background. The following environment variables are useful to config how Argilla connects to Redis:

- `ARGILLA_REDIS_URL`: A URL string that contains the necessary information to connect to a Redis instance (Default: `redis://localhost:6379/0`).

### Datasets

- `ARGILLA_LABEL_SELECTION_OPTIONS_MAX_ITEMS`: Set the number of maximum items to be allowed by label and multi label questions (Default: `500`).

- `ARGILLA_SPAN_OPTIONS_MAX_ITEMS`: Set the number of maximum items to be allowed by span questions (Default: `500`).

### Hugging Face

- `ARGILLA_SHOW_HUGGINGFACE_SPACE_PERSISTENT_STORAGE_WARNING`: When Argilla is running on Hugging Face Spaces you can use this environment variable to disable the warning message showed when persistent storage is disabled for the space (Default: `true`).

### Docker images only

- `REINDEX_DATASETS`: If `true` or `1`, the datasets will be reindexed in the search engine. This is needed when some search configuration changed or data must be refreshed (Default: `0`).

- `USERNAME`: If provided, the owner username. This can be combined with HF OAuth to define the argilla server owner (Default: `""`).

- `PASSWORD`: If provided, the owner password. If `USERNAME` and `PASSWORD` are provided, the owner user will be created with these credentials on the server startup (Default: `""`).

- `API_KEY`: The default user api key to user. If API_KEY is not provided, a new random api key will be generated (Default: `""`).

- `UVICORN_APP`: [Advanced] The name of the FastAPI app to run. This is useful when you want to extend the FastAPI app with additional routes or middleware. The default value is `argilla_server:app`.

## REST API docs

FastAPI also provides beautiful REST API docs that you can check at [http://localhost:6900/api/v1/docs](http://localhost:6900/api/v1/docs).
