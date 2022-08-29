# Telemetry
Rubrix uses telemetry to report anonymous usage and error information. As an open-source software, this type of information is important to improve and understand how the product is used.

## How to opt-out
You can opt-out of telemetry reporting using the `ENV` variable `RUBRIX_ENABLE_TELEMETRY` before launching the server. Setting this variable to `0` will completely disable telemetry reporting.

If you are a Linux/MacOs users you should run:

```bash
export RUBRIX_ENABLE_TELEMETRY=0
```

If you are Windows users you should run:

```bash
set RUBRIX_ENABLE_TELEMETRY=0
```

To opt-in again, you can set the variable to `1`.

## Why reporting telemetry
Anonymous telemetry information enable us to continously improve the product and detect recurring problems to better serve all users. We collect aggregated information about general usage and errors. We do NOT collect any information of users' data records, datasets, or metadata information.

## Sensitive data
We do not collect any piece of information related to the source data you store in Rubrix. We don't identify individual users. Your data does not leave your server at any time:

* No dataset record is collected.
* No dataset names or metadata are collected.

## Information reported
The following usage and error information is reported:

* The code of the raised error
* The `user-agent` and `accept-language` http headers
* Task name and number of records for bulk operations
* The rubrix version running the server
* The python version, e.g. `3.8.13`
* The system/OS name, such as `Linux`, `Darwin`, `Windows`
* The system’s release version, e.g. `Darwin Kernel Version 21.5.0: Tue Apr 26 21:08:22 PDT 2022; root:xnu-8020`
* The machine type, e.g. `AMD64`
* The underlying platform spec with as much useful information as possible. (ej. `macOS-10.16-x86_64-i386-64bit`)


This is performed by registering information from the following API methods:

* `/api/me`
* `/api/dataset/{name}/{task}:bulk`
* Raised server API errors


For transparency, you can inspect the source code where this is performed here (add link to the source).

If you have any doubts, don't hesitate to join our [Slack channel](https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g) or open a GitHub issue. We'd be very happy to discuss about how we can improve this.
