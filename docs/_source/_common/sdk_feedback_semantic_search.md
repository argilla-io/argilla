In the Python SDK, you can also get a list of feedback records that are semantically close to a given embedding with the `find_similar_records` method. These are the arguments of this function:

- `vector_name`: The `name` of the vector to use in the search.
- `value`: A vector to use for the similarity search in the form of a `List[float]`. It is necessary to include a `value` **or** a `record`.
- `record`: A `FeedbackRecord` to use as part of the search. It is necessary to include a `value` **or** a `record`.
- `max_results` (optional): The maximum number of results for this search. The default is `50`.

This returns a list of Tuples with the records and their similarity score (between 0 and 1).

```python
ds = rg.FeedbackDataset.from_argilla("my_dataset", workspace="my_workspace")

# using text embeddings
similar_records =  ds.find_similar_records(
    vector_name="my_vector",
    value=embedder_model.embeddings("My text is here")
    # value=embedder_model.embeddings("My text is here").tolist() # for numpy arrays
)

# using another record
similar_records =  ds.find_similar_records(
    vector_name="my_vector",
    record=ds.records[0],
    max_results=5
)

# work with the resulting tuples
for record, score in similar_records:
    ...
```

You can also combine filters and semantic search like this:

```python
similar_records = (dataset
    .filter_by(metadata=[rg.TermsMetadataFilter(values=["Positive"])])
    .find_similar_records(vector_name="vector", value=model.encode("Another text").tolist())
)
```
