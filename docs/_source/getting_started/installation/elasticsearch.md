
# Elasticsearch Configuration

This section explains advanced configurations to use Argilla with Elasticsearch instances or clusters.
(configure-elasticsearch-role-users)=
## Configure roles and users

If you have an Elasticsearch instance and want to share resources with other applications, you can easily configure it for Argilla.

All you need to take into account is:


* Argilla will create its ES indices with the following pattern `.argilla*`. It's recommended to create a new role (e.g., argilla) and provide it with all privileges for this index pattern.

* Argilla creates an index template for these indices, so you may provide related template privileges to this ES role.

Argilla uses the `ELASTICSEARCH` environment variable to set the ES connection.

You can provide the credentials using the following scheme:

```bash
http(s)://user:passwd@elastichost
```

Below you can see a screenshot for setting up a new *argilla* Role and its permissions:

![Argilla Role and permissions in ES](https://user-images.githubusercontent.com/2518789/142883104-f4f20cf0-34a0-47ff-8ee3-ab9f4644271c.png)


## Change index analyzers

By default, for indexing text fields, Argilla uses the `standard` analyzer for general search and the `whitespace`
analyzer for more exact queries (required by certain rules in the weak supervision module). If those analyzers
don't fit your use case, you can change them using the following environment variables:
`ARGILLA_DEFAULT_ES_SEARCH_ANALYZER` and `ARGILLA_EXACT_ES_SEARCH_ANALYZER`.

Note that provided analyzers names should be defined as built-in ones. If you want to use a
customized analyzer, you should create it inside an index_template matching Argilla index names (`.argilla*.records-v0),
and then provide the analyzer name using the specific environment variable.

## Reindex data

Sometimes updates require reindexing our dataset metrics and Elasticsearch, therefore we devised some [short documentation](../../guides/features/datasets) to show you how to do this from our Python client.
