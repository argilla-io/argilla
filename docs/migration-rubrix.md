# Migration from Rubrix to Argilla

If you have already running a Rubrix server and want to upgrade to the new Argilla server, this guide will help you understand and transition into Argilla.

## Python module and command

The module now is called `argilla` instead of `rubrix`, but the rest of the code remains fully compatible, so
if you have to updgrade some codebase, you should just replace the line:

`import rubrix...`

with the new module name

`import argilla...`


Equivalently, to launch the server:

````bash
python -m argilla
````

instead of

````bash
python -m rubrix
````

## Environment variables

All the environment variables have changed from using the prefix `RUBRIX_` to using the prefix `ARGILLA_`.
The `ELASTICSEARCH` and other non-prefixed variables are still available, but they will be removed in the future.
You should use `ARGILLA_` version instead.

The best to configure a new Argilla Server from Rubrix is just to duplicate all ENV variables for
both, Rubrix and Argilla instances. This will simplify a version rollback if needed.

## New Elasticsearch index naming conventions

Argilla also introduces a new name convention for the stored indices in Elasticsearch.

For the index pattern containing all created datasets, the new namespace is `ar.datasets`, instead of `.rubrix.datasets-v0`

For indices containing the dataset records, the new name convention is `ar.dataset.<dataset_id>`, instead of
`.rubrix.dataset.<datset_id>.records-v0`

## Enable migration process

By default, the new Argilla server won't check if datasets from a previous Rubrix instance exists.

If you want the new Argilla Server to detect previous Rubrix datasets and make them accessible into your Argilla Server instance you can set the `ARGILLA_ENABLE_MIGRATION` like this before starting the Argilla server:

```bash
ARGILLA_ENABLE_MIGRATION=1 python -m argilla
```

This will fetch info contained in the Rubrix instance `.rubrix.datasetsw-v0` index and
will copy the info into the new `ar.datasets` index.

Then, for each old rubrix index, will create an alias with new new name convention format.

This will allow you to work with previous Rubrix datasets from your new Argilla Server without duplicating information and still see the changes from your previous Rubrix Server.

This migration switch can help you with a more gradual transition into Argilla.

>:warning: New datasets created from argilla won't be visible from the old rubrix instance.

> 🚒 **We'd love to support you with this migration process. The easiest way is to contact us through the [Slack Community](https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g) or to open a GitHub issue**

