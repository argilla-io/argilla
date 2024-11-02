# Migration from Rubrix

If you have already running a Rubrix server and want to upgrade to the new Argilla server, this guide will help you understand and transition into Argilla.

## Python module and command

The module now is called `argilla` instead of `rubrix`, but the rest of the code remains fully compatible, so
if you have to upgrade some codebase, you should just replace the line:

`import rubrix...`

with the new module name

`import argilla...`

Equivalently, to launch the server:

````bash
argilla server start
````

instead of

````bash
python -m rubrix
````

## Environment variables

All the environment variables have changed from using the prefix `RUBRIX_` to using the prefix `ARGILLA_`.

.. warning::
  From version `1.13.0`, the support for non-prefixed environment variables has been removed. All environment variables must be prefixed with `ARGILLA_`.

The best way to configure a new Argilla Server from Rubrix is just to duplicate all ENV variables for
both, Rubrix and Argilla instances. This will simplify a version rollback if needed.

## New Elasticsearch index naming conventions

Argilla also introduces a new name convention for the stored indices in Elasticsearch.

For the index pattern containing all created datasets, the new namespace is `ar.datasets`, instead of `.rubrix.datasets-v0`

For indices containing the dataset records, the new name convention is `ar.dataset.<dataset_id>`, instead of
`.rubrix.dataset.<datset_id>.records-v0`

## Enable migration process

By default, the new Argilla server won't check if datasets from a previous Rubrix instance exist.

If you want the new Argilla Server to detect previous Rubrix datasets and make them accessible into your Argilla Server instance you can set the `ARGILLA_ENABLE_MIGRATION` like this before starting the Argilla server:

```bash
ARGILLA_ENABLE_MIGRATION=1 argilla server start
```

This will fetch info contained in the Rubrix instance `.rubrix.datasetsw-v0` index and
will copy the info into the new `ar.datasets` index.

Then, for each old rubrix index, will create an alias with new naming convention format.

This will allow you to work with previous Rubrix datasets from your new Argilla Server without duplicating information and still see the changes from your previous Rubrix Server.

This migration switch can help you with a more gradual transition into Argilla.

>:warning: New datasets created from argilla won't be visible from the old rubrix instance.

> 🚒 **We'd love to support you with this migration process. The easiest way is to contact us through the [Slack Community](http://hf.co/join/discord) or to open a GitHub issue**

## Old versions of Rubrix

If you need to visit the old Rubrix documentation, you can follow this [link](https://rubrix.readthedocs.io/en/v0.18.0/)
