# Search input

This component enables:

1. **Full-text queries** over all record ``inputs``.

2. Queries using **Elasticsearch's query DSL** with the [query string syntax](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#query-string-syntax). Some examples are:
    -``inputs.text:(women AND feminists)`` : records containing the words "women" AND "feminist" in the inputs.text field.

    -``inputs.text:(NOT women)`` : records NOT containing women in the inputs.text field.

    -``inputs.hypothesis:(not OR don't)`` : records containing the word "not" or the phrase "don't" in the inputs.hypothesis field.

    -``metadata.format:pdf AND metadata.page_number>1`` : records with metadata.format equals pdf and with metadata.page_number greater than 1.

    -``NOT(_exists_:metadata.format)`` : records that don't have a value for metadata.format.

    -``predicted_as:(NOT Sports)`` : records which are not predicted with the label ``Sports``, this is useful when you have many target labels and want to exclude only some of them.

![Search input with Elasticsearch DSL query string](images/active_query_params.png)

**NOTE**: Elasticsearch's query DSL supports **escaping special characters** that are part of the query syntax. The current list special characters are:

| ----------- |
| ``+ - && || ! ( ) { } [ ] ^ " ~ * ? : \`` |

To escape these character use the \\ before the character. For example to search for (1+1):2 use the query ``\(1\+1\)\:2``.

## Elasticsearch fields

Shown below is a summary of available fields that can be used for the query DSL, as well as for building **Kibana Dashboards**— common fields to all record types, and those specific to certain record types:

| Common fields   | Text classification fields  | Token classification fields  |
| -------------   | -----------------------     | -----------------------      |
| Annotated_as    | inputs.*                    | tokens                       |
| Annotated_by    | score                       |                              |
| event_timestamp |                             |                              |
| id              |                             |                              |
| last_updated    |                             |                              |
| metadata.*      |                             |                              |
| multi_label     |                             |                              |
| predicted       |                             |                              |
| predicted_as    |                             |                              |
| predicted_by    |                             |                              |
| status          |                             |                              |
| words           |                             |                              |
