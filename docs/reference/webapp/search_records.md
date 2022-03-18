# Search Records

<video width="100%" controls><source src="../../_static/reference/webapp/search_records.mp4" type="video/mp4"></video>

The search bar in Rubrix is driven by Elasticsearch's powerful [query string syntax](https://www.elastic.co/guide/en/elasticsearch/reference/7.10/query-dsl-query-string-query.html#query-string-syntax).
It allows you to perform simple fuzzy searches of words and phrases, or complex queries taking full advantage of Rubrix's data model.

## Search fields

An important concept when searching with Elasticsearch is the *field* concept.
Every search in Rubrix is directed to a specific field of the record's underlying data model.
For example, writing `text:fox` in the search bar will search for records with the word `fox` in the field `text`.

If you do not provide any fields in your query string, by default Rubrix will search in the fields `word` and `word.extended`.
For a complete list of available fields, their content and their type, have a look at the field glossary below.

```{note}
The default behavior when not specifying any fields in the search, will likely change in the near future.
We recommend emulating the future behavior by using the `text` field for your default searches, that is change `brown fox` to `text:(brown fox)`, for example.
```

## `text` and `text.exact`

The (arguably) most important fields are the `text` and `text.exact` fields.
They both contain the text of the records, however in two different forms:

- the `text` field uses Elasticsearch's [standard analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/7.10/analysis-standard-analyzer.html) that ignores capitalization and removes most of the punctuatio;
- the `text.exact` field uses the [whitespace analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/7.10/analysis-whitespace-analyzer.html) that differentiates between lower and upper case, and does take into account punctuation;

Let's have a look at a few examples.
Suppose we have 2 records with the following text:

1. *The quick brown fox jumped over the lazy dog.*
2. *THE DOG HATED THE FOX!*

The queries `text:dog.` and `text.fox` would match both of the records, while the queries `text.exact:dog` and `text.exact:fox` would match none.
However, the queries `text.exact:dog.` and `text.exact:fox` would both yield only the first record, while the queries `text.exact:DOG` or `text.exact:FOX!` would return the second record.
You can see how the `text.exact field can be used to search in a more fine-grained manner.

## Words and phrases

## Field types

### metadata fields

### filters as query string

## Combine fields

## Query string features

### Escaping special characters

## Field glossary





You can search records by using full-text queries (a normal search), or by Elasticsearch with its [query string syntax](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#query-string-syntax).

- Using the `text` and `text.exact` fields
  + standard and whitespace analyzers
  + Examples: `text:The phrase` `text.exact:THE PHRASE`

- Default search by `words` and `words.extended`
  + Search are based on both fields. The default search use both fields.
  + `words` and `words.extended` deprecation disclaims
  + ->  promote to prefixed `text:` searches instead default

- Using other fields in search:
  + Selective inputs search for text classification (`inputs.*` and `inputs.*.exact`)
  + Metadata values: `metadata.split: train` *ONLY AS KEYWORD

- Filters as query text search
  + You can use filters in search
  + `predicted_as: POSITIVE`
  + `status:Validated`
  + `annotated_by: john`

- Combining fields (AND OR NOT....)
  + You can use boolean operator to compose fields or terms in search
  + Default operator for keywords is the AND operator
  + `text:(Mike OR Anna)`
  + `annotated_as: john OR status:Default`
  + `NOT(_exists_:predicted_as)`

- Some interesting query dsl features:
  + Regular patterns
    + `text:/joh?n(ath[oa]n)/`
  + Ranges
    + `score:[0.7 TO 0.8]`
  + Phrase search
    + `text:"the phrase your're looking for"`
  + fuzziness
    + `rubri~`
  + boosting
    + `inputs.subject:Rubrix^2 AND inputs.body:better`

- Fields glossary (and kind)
  - TODO

1. **Full-text queries** over all record `inputs`.

2. Queries using **Elasticsearch's query DSL** with the [query string syntax](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#query-string-syntax). Some examples are: -`inputs.text:(women AND feminists)` : records containing the words "women" AND "feminist" in the inputs.text field.

   -`inputs.text:(NOT women)` : records NOT containing women in the inputs.text field.

   -`inputs.hypothesis:(not OR don't)` : records containing the word "not" or the phrase "don't" in the inputs.hypothesis field.

   -`metadata.format:pdf AND metadata.page_number>1` : records with metadata.format equals pdf and with metadata.page_number greater than 1.

   -`NOT(_exists_:metadata.format)` : records that don't have a value for metadata.format.

   -`predicted_as:(NOT Sports)` : records which are not predicted with the label `Sports`, this is useful when you have many target labels and want to exclude only some of them.

![Search input with Elasticsearch DSL query string](../../_static/reference/webapp/active_query_params.png)

**NOTE**: Elasticsearch's query DSL supports **escaping special characters** that are part of the query syntax. The current list special characters are:

`+ - && || ! ( ) { } [ ] ^ " ~ * ? : \`

To escape these character use the \\ before the character. For example to search for (1+1):2 use the query `\(1\+1\)\:2`.

In both **Annotation** and **Exploration** modes, the search bar is placed in the upper left-hand corner. To search something, users must type one or several words (or a query) and click the **Intro** button.

Note that this feature also works as a kind of filter. If users search something, it is possible to explore and/or annotate the results obtained. [Filters](filter_records.md) can be applied.

## Elasticsearch fields

Shown below is a summary of available fields that can be used for the query DSL, as well as for building **Kibana Dashboards**— common fields to all record types, and those specific to certain record types:

| Common fields   | Text classification fields | Token classification fields |
| --------------- | -------------------------- | --------------------------- |
| Annotated_as    | inputs.\*                  | tokens                      |
| Annotated_by    | score                      |                             |
| event_timestamp |                            |                             |
| id              |                            |                             |
| last_updated    |                            |                             |
| metadata.\*     |                            |                             |
| multi_label     |                            |                             |
| predicted       |                            |                             |
| predicted_as    |                            |                             |
| predicted_by    |                            |                             |
| status          |                            |                             |
| words           |                            |                             |
| words.extended  |                            |                             |

With this component, users are able to search specific information on the dataset, either by **full-text queries** or by queries using **Elasticsearch**.
