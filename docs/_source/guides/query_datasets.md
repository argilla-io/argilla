# 🔎 Query datasets

The search in Argilla is driven by Elasticsearch's powerful [query string syntax](https://www.elastic.co/guide/en/elasticsearch/reference/7.10/query-dsl-query-string-query.html#query-string-syntax).
It allows you to perform simple fuzzy searches of words and phrases, or complex queries taking full advantage of Argilla's data model.

The same query can be used in the search bar of the Argilla web app, or with the Python client as optional arguments.


```python
import argilla as rg

rg.load("my_dataset", query="text.exact:example")
```

## Search fields

An important concept when searching with Elasticsearch is the *field* concept.
Every search term in Argilla is directed to a specific field of the record's underlying data model.
For example, writing `text:fox` in the search bar will search for records with the word `fox` in the field `text`.

If you do not provide any fields in your query string, by default Argilla will search in the `text` field.
For a complete list of available fields and their content, have a look at the field glossary below.

```{note}
The default behavior when not specifying any fields in the query string changed in version `>=0.16.0`.
Before this version, Argilla searched in a mixture of the the deprecated `word` and `word.extended` fields that allowed searches for special characters like `!` and `.`.
If you want to search for special characters now, you have to specify the `text.exact` field.
For example, this is the query if you want to search for words with an exclamation mark in the end: `text.exact:*\!`

If you do not retrieve any results after a version update, you should use the `words` and `words.extended` fields in your search query for old datasets instead of the `text` and `text.exact` ones.
```

## `text` and `text.exact`

The (arguably) most important fields are the `text` and `text.exact` fields.
They both contain the text of the records, however in two different forms:

- the `text` field uses Elasticsearch's [standard analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/7.10/analysis-standard-analyzer.html) that ignores capitalization and removes most of the punctuation;
- the `text.exact` field uses the [whitespace analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/7.10/analysis-whitespace-analyzer.html) that differentiates between lower and upper case, and does take into account punctuation;

Let's have a look at a few examples.
Suppose we have 2 records with the following text:

1. *The quick brown fox jumped over the lazy dog.*
2. *THE LAZY DOG HATED THE QUICK BROWN FOX!*

Now consider these queries:

- `text:dog.` or `text:fox`: matches both of the records.
- `text.exact:dog` or `text.exact:FOX`: matches none of the records.
- `text.exact:dog.` or `text.exact:fox`: matches only the first record.
- `text.exact:DOG` or `text.exact:FOX\!`: matches only the second record.

You can see how the `text.exact` field can be used to search in a more fine-grained manner.

### TextClassificationRecord's `inputs`

For [text classification records](../../reference/python/python_client.rst) you can take advantage of the multiple `inputs` when performing a search.
For example, if we uploaded records with `inputs={"subject": ..., "body": ...}`, you can direct your searches to only one of those inputs by specifying the `inputs.subject` or `inputs.body` field in your query.
So to look for records in which the *subject* contains the word *news*, you would search for

- `inputs.subject:news`

Again, as with the `text` field, you can also use the white space analyzer to perform more fine-grained searches by specifying the `exact` field:

- `inputs.subject.exact:NEWS`

## Words and phrases

Apart from single words you can also search for *phrases* by surrounding multiples words with double quotes.
This searches for all the words in the phrase, in the same order.

If we take the two examples from above, then following query will only return the second example:

- `text:"lazy dog hated"`

## Metadata fields

You also have the metadata of your records available when performing a search.
Imagine you provided the split to which the record belongs to as metadata, that is `metadata={"split": "train"}` or `metadata={"split": "test"}`.
Then you could only search your training data by specifying the corresponding field in your query:

- `metadata.split:train`

Metadata are indexed as keywords.
This means you cannot search for single words in them, and capitalization and punctuations are taken into account.
You can, however, use wild cards.

### Non-searchable metadata fields

If your intention is to only store metadata with records and not use it for searches, you can achieve this by defining
the metadata field with a leading underscore. For instance, if you use `metadata._my_hidden_field`, the field will be
accessible at the record level, but it won't be used in searches.

## Vector fields

It is also possible to query the presense of vector field. Imagine you only want to include records with `vectors={"vector_1": vector_1}`. You can then define a query `vectors.vector_1: *`.
## Filters as query string

Just like the metadata, you can also use the filter fields in you query.
A few examples to emulate the filters in the query string are:

- `status:Validated`
- `annotated_as:HAM`
- `predicted_by:Model A`

The field values are treated as keywords, that is you cannot search for single words in them, and capitalization and punctuations are taken into account.
You can, however, use wild cards.

## Combine terms and fields

You can combine an arbitrary amount of terms and fields in your search using the familiar boolean operators `AND`, `OR` and `NOT`.
Following examples showcase the power of these operators:

- `text:(quick AND fox)`: Returns records that contain the word *quick* and *fox*. The `AND` operator is the default operator, so `text:(quick fox)` is equivalent.
- `text:(quick OR brown)`: Returns records that contain either the word *quick* or *brown*.
- `text:(quick AND fox AND NOT news)`: Returns records that contain the words *quick* and *fox*, **and do not** contain *news*.
- `metadata.split:train AND text:fox`: Returns records that contain the word *fox* and that have a metadata *"split: train"*.
- `NOT _exists_:metadata.split` : Returns records that don't have a metadata *split*.

## Query string features

The query string syntax has many powerful features that you can use to create complex searches.
Following is just a hand selected subset of the many features you can look up on the official [Elasticsearch documentation](https://www.elastic.co/guide/en/elasticsearch/reference/7.10/query-dsl-query-string-query.html).

### Wildcards

Wildcard searches can be run on individual search terms, using `?` to replace a single character, and `*` to replace zero or more characters:

- `text:(qu?ck bro*)`
- `text.exact:"Lazy Dog*"`: Matches, for example, *"Lazy Dog"*, *"Lazy Dog."*, or *"Lazy Dogs"*.
- `inputs.\*:news`: Searches all input fields for the word *news*.

### Regular expressions

Regular expression patterns can be embedded in the query string by wrapping them in forward slashes "/":

- `text:/joh?n(ath[oa]n)/`: Matches *jonathon*, *jonathan*, *johnathon*, and *johnathan*.

The supported regular expression syntax is explained on the official [Elasticsearch documentation](https://www.elastic.co/guide/en/elasticsearch/reference/7.10/regexp-syntax.html).

### Fuzziness

You can search for terms that are similar to, but not exactly like the search terms, using the *fuzzy* operator.
This is useful to cover human misspellings:

- `text:quikc~`: Matches quick and quikc.

### Ranges

Ranges can be specified for date, numeric or string fields.
Inclusive ranges are specified with square brackets and exclusive ranges with curly brackets:

- `score:[0.5 TO 0.6]`
- `score:{0.9 TO *}`

#### Datetime Ranges

Datetime ranges are a special kind of range queries that can be defined for the `event_timestamp` and `last_updated` fields.
The formatting is similar to normal range queries, but they require an iso-formatted datetime, which can be ontained via `datetime.now().isoformat()`, resulting in `1984-01-01T01:01:01.000000`. Note that the `*` can be used inter-changebly for the end of time or beginning of time.

- `event_timestamp:[1984-01-01T01:01:01.000000 TO *]`
- `last_updated:{* TO 1984-01-01T01:01:01.000000}`

### Escaping special characters

The query string syntax has some reserved characters that you need to escape if you want to search for them.
The reserved characters are: `+ - = && || > < ! ( ) { } [ ] ^ " ~ * ? : \ /`
For instance, to search for *"(1+1)=2"* you need to write:

- `text:\(1\+1\)\=2`

## Field glossary

This is a table with available fields that you can use in your query string:

| Field name                               | Description                           | TextClass.                                  | TokenClass.                                 | TextGen.                                    |
| ---------------------------------------- | ------------------------------------- | ------------------------------------------- | ------------------------------------------- | ------------------------------------------- |
| annotated_as                             | annotation                            | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> |
| annotated_by                             | annotation agent                      | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> |
| event_timestamp                          | timestamp                             | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> |
| id                                       | id                                    | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> |
| inputs.\*                                | inputs                                | <p style="text-align: center;">&#10004;</p> |                                             |                                             |
| metadata.\*                              | metadata                              | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> |
| vectors.\*                               | vectors                               | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> |
| last_updated                             | date of the last update               | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> |
| predicted_as                             | prediction                            | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> |
| predicted_by                             | prediction agent                      | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> |
| score                                    | prediction score                      | <p style="text-align: center;">&#10004;</p> |                                             |                                             |
| status                                   | status                                | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> |
| text                                     | text, standard analyzer               | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> |
| text.exact                               | text, whitespace analyzer             | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> |
| tokens                                   | tokens                                |                                             | <p style="text-align: center;">&#10004;</p> |                                             |
| -                                        | -                                     | -                                           | -                                           | -                                           |
| metrics.text_lengt                       | Input text length                     | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> | <p style="text-align: center;">&#10004;</p> |
| metrics.tokens.idx                       | Token idx in record                   |                                             | <p style="text-align: center;">&#10004;</p> |                                             |
| metrics.tokens.value                     | Text of the token                     |                                             | <p style="text-align: center;">&#10004;</p> |                                             |
| metrics.tokens.char_start                | Start char idx of token               |                                             | <p style="text-align: center;">&#10004;</p> |                                             |
| metrics.tokens.char_end                  | End char idx of token                 |                                             | <p style="text-align: center;">&#10004;</p> |                                             |
| metrics.annotated.mentions.value         | Text of the mention (annotation)      |                                             | <p style="text-align: center;">&#10004;</p> |                                             |
| metrics.annotated.mentions.label         | Label of the mention (annotation)     |                                             | <p style="text-align: center;">&#10004;</p> |                                             |
| metrics.annotated.mentions.score         | Score of the mention (annotation)     |                                             | <p style="text-align: center;">&#10004;</p> |                                             |
| metrics.annotated.mentions.capitalness   | Mention capitalness (annotation)      |                                             | <p style="text-align: center;">&#10004;</p> |                                             |
| metrics.annotated.mentions.density       | Local mention density (annotation)    |                                             | <p style="text-align: center;">&#10004;</p> |                                             |
| metrics.annotated.mentions.tokens_length | Mention length in tokens (annotation) |                                             | <p style="text-align: center;">&#10004;</p> |                                             |
| metrics.annotated.mentions.chars_length  | Mention length in chars (annotation)  |                                             | <p style="text-align: center;">&#10004;</p> |                                             |
| metrics.annotated.tags.value             | Text of the token (annotation)        |                                             | <p style="text-align: center;">&#10004;</p> |                                             |
| metrics.annotated.tags.tag               | IOB tag (annotation)                  |                                             | <p style="text-align: center;">&#10004;</p> |                                             |
| metrics.predicted.mentions.value         | Text of the mention (prediction)      |                                             | <p style="text-align: center;">&#10004;</p> |                                             |
| metrics.predicted.mentions.label         | Label of the mention (prediction)     |                                             | <p style="text-align: center;">&#10004;</p> |                                             |
| metrics.predicted.mentions.score         | Score of the mention (prediction)     |                                             | <p style="text-align: center;">&#10004;</p> |                                             |
| metrics.predicted.mentions.capitalness   | Mention capitalness (prediction)      |                                             | <p style="text-align: center;">&#10004;</p> |                                             |
| metrics.predicted.mentions.density       | Local mention density (prediction)    |                                             | <p style="text-align: center;">&#10004;</p> |                                             |
| metrics.predicted.mentions.tokens_length | Mention length in tokens (prediction) |                                             | <p style="text-align: center;">&#10004;</p> |                                             |
| metrics.predicted.mentions.chars_length  | Mention length in chars (prediction)  |                                             | <p style="text-align: center;">&#10004;</p> |                                             |
| metrics.predicted.tags.value             | Text of the token (prediction)        |                                             | <p style="text-align: center;">&#10004;</p> |                                             |
| metrics.predicted.tags.tag               | IOB tag (prediction)                  |                                             | <p style="text-align: center;">&#10004;</p> |                                             |

