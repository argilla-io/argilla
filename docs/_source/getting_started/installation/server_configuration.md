# Server configuration

This section explains advanced operations and settings for running the Argilla Server and Argilla Python Client.

By default, the Argilla Server will look for your Elasticsearch (ES) endpoint at `http://localhost:9200`. You can customize this by setting the `ARGILLA_ELASTICSEARCH` environment variable. Have a look at the list of available [environment variables](#environment-variables) to further configure the Argilla server.

## Launching
### Using a proxy

If you run argilla behind a proxy by adding some extra prefix to expose the service, you should setup the `ARGILLA_BASE_URL`
environment variable to properly route requests to server application.

For example, if your proxy exposes argilla in the URL `https://my-proxy/custom-path-for-argilla`,  you should launch the
argilla server with `ARGILLA_BASE_URL=/custom-path-for-argilla`.

### with `uvicorn`

Since the Argilla Server is built on FastAPI, you can launch it using `uvicorn`:

```bash
uvicorn argilla:app
```

:::{note}
For more details about fastapi and uvicorn, see [here](https://fastapi.tiangolo.com/deployment/manually/#run-a-server-manually-uvicorn).
:::


## Environment variables

You can set following environment variables to further configure your server and client.

### Server

- `ARGILLA_ELASTICSEARCH`: URL of the connection endpoint of the Elasticsearch instance (Default: `http://localhost:9200`).

- `ARGILLA_ELASTICSEARCH_SSL_VERIFY`: If "False", disables SSL certificate verification when connection to the Elasticsearch backend.

- `ARGILLA_ELASTICSEARCH_CA_PATH`: Path to CA cert for ES host. For example: `/full/path/to/root-ca.pem` (Optional)

- `ARGILLA_BASE_URL`: If you want to launch the argilla server in an specific base path other than /, you should setup this environment variable. This can be useful when running argilla behind a proxy that adds a prefix path to route the service (Default: "/").

- `ARGILLA_NAMESPACE`: A prefix used to manage Elasticsearch indices. You can use this namespace to use the same Elasticsearch instance for several independent Argilla instances.

- `ARGILLA_DEFAULT_ES_SEARCH_ANALYZER`: Default analyzer for textual fields excluding the metadata (Default: "standard").

- `ARGILLA_EXACT_ES_SEARCH_ANALYZER`: Default analyzer for `*.exact` fields in textual information (Default: "whitespace").

- `ARGILLA_METADATA_FIELDS_LIMIT`: Max number of fields in the metadata (Default: 50, max: 100).

- `ARGILLA_METADATA_FIELD_LENGTH`: Max length supported for the string metadata fields. Higher values will be truncated. Abusing this may lead to Elastic performance issues (Default: 128).

- `CORS_ORIGINS`: List of host patterns for CORS origin access.

- `DOCS_ENABLED`: If False, disables openapi docs endpoint at */api/docs*.

- `ARGILLA_ENABLE_TELEMETRY`: If False, disables telemetry for usage metrics.


### Client

- `ARGILLA_API_URL`: The default API URL when calling {meth}`argilla.init`.

- `ARGILLA_API_KEY`: The default API key when calling {meth}`argilla.init`.

- `ARGILLA_WORKSPACE`: The default workspace when calling {meth}`argilla.init`.

## REST API docs

FastAPI also provides beautiful REST API docs that you can check at [http://localhost:6900/api/docs](http://localhost:6900/api/docs).
