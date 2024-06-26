# Telemetry
Argilla uses telemetry to report anonymous usage and error information. As an open-source software, this type of information is important to improve and understand how the product is used.

## How to opt out
You can opt out of telemetry reporting using the `ENV` variable `ARGILLA_ENABLE_TELEMETRY` before launching the server. Setting this variable to `0` will completely disable telemetry reporting.

If you are a Linux/MacOs user, you should run:

```bash
export ARGILLA_ENABLE_TELEMETRY=0
```

If you are a Windows user, you should run:

```bash
set ARGILLA_ENABLE_TELEMETRY=0
```

To opt in again, you can set the variable to `1`.

## Why reporting telemetry
Anonymous telemetry information enables us to continuously improve the product and detect recurring problems to better serve all users. We collect aggregated information about general usage and errors. We do NOT collect any information on users' data records, datasets, or metadata information.

## Sensitive data
We do not collect any piece of information related to the source data you store in Argilla. We don't identify individual users. Your data does not leave your server at any time:

* No dataset record is collected.
* No dataset names or metadata are collected.

## Information reported
The following usage and error information is reported:

* The code of the raised error and the entity type related to the error, if any (Dataset, Workspace,...)
* The `user-agent` and `accept-language` http headers
* Task name and number of records for bulk operations
* An anonymous generated user uuid
* The Argilla version running the server
* The Python version, e.g. `3.8.13`
* The system/OS name, such as `Linux`, `Darwin`, `Windows`
* The system’s release version, e.g. `Darwin Kernel Version 21.5.0: Tue Apr 26 21:08:22 PDT 2022; root:xnu-8020`
* The machine type, e.g. `AMD64`
* The underlying platform spec with as much useful information as possible. (eg. `macOS-10.16-x86_64-i386-64bit`)
* The type of deployment: `quickstart` or `server`
* The dockerized deployment flag: `True` or `False`

This is performed by registering information from the following API methods:

* `GET /api/me`
* `POST /api/dataset/{name}/{task}:bulk`
* `POST /api/users`
* Raised server API errors

Additionally, we report the usage of integration for our Python library:

* `ArgillaTrainer` framework usage and NLP task-type.

We also report the usage of our tutorials by `tutorial_running`:

* The tutorial usage count and its name.

For transparency, you can inspect the source code where this is performed [here](https://github.com/argilla-io/argilla/blob/main/src/argilla/utils/telemetry.py).

If you have any doubts, don't hesitate to join our [Discord channel](http://hf.co/join/discord) or open a GitHub issue. We'd be very happy to discuss how we can improve this.
