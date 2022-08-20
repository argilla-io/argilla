# Telemetry
Rubrix uses telemetry to report anonymous usage and error information. As an open-source software, this type of information is important to improve and understand how the product is used.

## How to opt-out
You can opt-out of telemetry reporting using the `ENV` variable `var_name_tbd` before launching the server. Setting this variable to `false` will completely disable telemetry reporting.

If you are a Linux/MacOs users you should run:

```bash
bash command to disable telemetry
```

If you are Windows users you should run:

```bash
bash command to disable telemetry
```

To opt-in again, you can set the variable to `true`.

## Why reporting telemetry
Anonymous telemetry information enable us to continously improve the product and detect recurring problems to better serve all users. We collect aggregated information about general usage and errors. We do NOT collect any information of users' data records, datasets, or metadata information.

## Sensitive data
We do not collect any piece of information related to the source data you store in Rubrix. We don't identify individual users. Your data does not leave your server at any time:

* No dataset record is collected.
* No dataset names or metadata are collected.

## Information reported
The following usage and error information is reported:


* exhaustive ist of fields/info
* ...

This is performed by registering information from the following API methods:

* `/api/me`
* `/api/dataset/.../bulk`
* API errors


For transparency, you can inspect the source code where this is performed here (add link to the source).

If you have any doubts, don't hesitate to join our [Slack channel](https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g) or open a GitHub issue. We'd be very happy to discuss about how we can improve this.
