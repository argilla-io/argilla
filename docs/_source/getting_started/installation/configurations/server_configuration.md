# Server configuration

This section explains advanced operations and settings for running the Argilla Server and Argilla Python Client.

By default, the Argilla Server will look for your Elasticsearch (ES) endpoint at `http://localhost:9200`. You can customize this by setting the `ARGILLA_ELASTICSEARCH` environment variable. Have a look at the list of available [environment variables](#environment-variables) to further configure the Argilla server.

From the Argilla version `1.19.0`, you must set up the search engine manually to work with Feedback datasets. You should set the
environment variable `ARGILLA_SEARCH_ENGINE=opensearch` or `ARGILLA_SEARCH_ENGINE=elasticsearch` depending on the backend you're using
The default value for this variable is set to `elasticsearch`. The minimal version for Elasticsearch is `8.5.0`, and for Opensearch is `2.4.0`.
Please, review your backend and upgrade it if necessary.

:::{warning}
For vector search in OpenSearch, the filtering applied is using a `post_filter` step, since there is a bug that makes queries fail using filtering + knn from Argilla.
See https://github.com/opensearch-project/k-NN/issues/1286

This may result in unexpected results when combining filtering with vector search with this engine.
:::

## Launching

### Using a proxy

If you run Argilla behind a proxy by adding some extra prefix to expose the service, you should set the `ARGILLA_BASE_URL`
environment variable to properly route requests to the server application.

For example, if your proxy exposes Argilla in the URL `https://my-proxy/custom-path-for-argilla`, you should launch the
Argilla server with `ARGILLA_BASE_URL=/custom-path-for-argilla`.

NGINX and Traefik have been tested and are known to work with Argilla:

- [NGINX example](https://github.com/argilla-io/argilla/tree/main/docker/nginx)
- [Traefik example](https://github.com/argilla-io/argilla/tree/main/docker/traefik)

### with `uvicorn`

Since the Argilla Server is built on FastAPI, you can launch it using `uvicorn`:

```bash
uvicorn argilla_server:app --port 6900
```

:::{note}
For more details about FastAPI and uvicorn, see [here](https://fastapi.tiangolo.com/deployment/manually/#run-a-server-manually-uvicorn).

You can also visit the uvicorn official documentation [here](https://www.uvicorn.org/#usage).
:::

## Environment variables

You can set the following environment variables to further configure your server and client.

### Server

#### FastAPI

- `ARGILLA_HOME_PATH`: The directory where Argilla will store all the files needed to run. If the path doesn't exist it will be automatically created (Default: `~/.argilla`).

- `ARGILLA_BASE_URL`: If you want to launch the Argilla server in a specific base path other than /, you should set up this environment variable. This can be useful when running Argilla behind a proxy that adds a prefix path to route the service (Default: "/").

- `ARGILLA_CORS_ORIGINS`: List of host patterns for CORS origin access.

- `ARGILLA_DOCS_ENABLED`: If False, disables openapi docs endpoint at _/api/docs_.

- `ARGILLA_ENABLE_TELEMETRY`: If False, disables telemetry for usage metrics.

#### SQLite and PostgreSQL

- `ARGILLA_DATABASE_URL`: A URL string that contains the necessary information to connect to a database. Argilla uses SQLite by default, PostgreSQL is also officially supported (Default: `sqlite:///$ARGILLA_HOME_PATH/argilla.db?check_same_thread=False`).

#### SQLite

The following environment variables are useful only when SQLite is used:

- `ARGILLA_DATABASE_SQLITE_TIMEOUT`: How many seconds the connection should wait before raising an `OperationalError` when a table is locked. If another connection opens a transaction to modify a table, that table will be locked until the transaction is committed. (Defaut: `15` seconds).

#### PostgreSQL

The following environment variables are useful only when PostgreSQL is used:

- `ARGILLA_DATABASE_POSTGRESQL_POOL_SIZE`: The number of connections to keep open inside the database connection pool (Default: `15`).

- `ARGILLA_DATABASE_POSTGRESQL_MAX_OVERFLOW`: The number of connections that can be opened above and beyond `ARGILLA_DATABASE_POSTGRESQL_POOL_SIZE` setting (Default: `10`).

#### Elasticsearch and Opensearch

- `ARGILLA_ELASTICSEARCH`: URL of the connection endpoint of the Elasticsearch instance (Default: `http://localhost:9200`).

- `ARGILLA_SEARCH_ENGINE`: (Only for Feedback datasets) Search engine to use. Valid values are "elasticsearch" and "opensearch" (Default: "elasticsearch").

- `ARGILLA_ELASTICSEARCH_SSL_VERIFY`: If "False", disables SSL certificate verification when connecting to the Elasticsearch backend.

- `ARGILLA_ELASTICSEARCH_CA_PATH`: Path to CA cert for ES host. For example: `/full/path/to/root-ca.pem` (Optional)

- `ARGILLA_NAMESPACE`: A prefix used to manage Elasticsearch indices. You can use this namespace to use the same Elasticsearch instance for several independent Argilla instances.

- `ARGILLA_DEFAULT_ES_SEARCH_ANALYZER`: Default analyzer for textual fields excluding the metadata (Default: "standard").

- `ARGILLA_EXACT_ES_SEARCH_ANALYZER`: Default analyzer for `*.exact` fields in textual information (Default: "whitespace").

- `ARGILLA_METADATA_FIELDS_LIMIT`: Max number of fields in the metadata (Default: 50, max: 100).

- `ARGILLA_METADATA_FIELD_LENGTH`: Max length supported for the string metadata fields. Higher values will be truncated. Abusing this may lead to Elastic performance issues (Default: 128).

### Feedback Datasets

- `ARGILLA_LABEL_SELECTION_OPTIONS_MAX_ITEMS`: Set the number of maximum items to be allowed by label and multi label questions (Default: `500`).

- `ARGILLA_SPAN_OPTIONS_MAX_ITEMS`: Set the number of maximum items to be allowed by span questions (Default: `500`).

### Hugging Face

- `ARGILLA_SHOW_HUGGINGFACE_SPACE_PERSISTENT_STORAGE_WARNING`: When Argilla is running on Hugging Face Spaces you can use this environment variable to disable the warning message showed when persistent storage is disabled for the space (Default: `true`).

### Client

- `ARGILLA_API_URL`: The default API URL when calling {meth}`argilla.init`.

- `ARGILLA_API_KEY`: The default API key when calling {meth}`argilla.init`.

- `ARGILLA_WORKSPACE`: The default workspace when calling {meth}`argilla.init`.

## REST API docs

FastAPI also provides beautiful REST API docs that you can check at [http://localhost:6900/api/docs](http://localhost:6900/api/docs).
