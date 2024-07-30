# ⏲️ Job Scheduling and Callbacks

## Feedback Dataset

```{note}
The `FeedbackDataset` does not offer support for job scheduling as of now. If you would like to use it, you will need to use one of the other datasets. To get more info about the dataset differences, you can have a look [here](/practical_guides/choose_dataset).
```

## Other datasets

This guide gives you a brief introduction to Argilla Listeners. Argilla Listeners enables you to build fine-grained complex workflows as background processes, like a low-key alternative to job scheduling directly integrated with Argilla.

The main goal facilitates the user to define and customize their Argilla experience. Note that the tutorial about [active learning with small-text](/tutorials/notebooks/training-textclassification-smalltext-activelearning.ipynb) is a great example of how powerful listeners can be. Alternatively, you can check the [Python Client](/reference/python/python_listeners.rst) to get acquainted.


<div class="alert alert-info">
This feature is experimental, you can expect some changes in the Python API. Please report on Github any issues you encounter. Also, Jupyter Notebooks might need to be completely restarted to ensure all background processes are properly stopped.
</div>

### Install dependencies

For using listeners you need to install the following dependencies:

```python
%pip install argilla[listeners] -qqq
```

### Basics

Listeners are decorators and wrap about a function that you would like to schedule. By defining a `query`, the `update_records` function gets two variables: 1) the `records` that we get from the dataset and query, and 2) the `ctx` that contains function parameters like `query` and `dataset`.

```python
import argilla as rg
from argilla.listeners import listener

@listener(
    dataset="my_dataset", # dataset to get record from
    query="lucene query", # https://docs.v1.argilla.io/en/latest/guides/query_datasets.html
    execution_interval_in_seconds=3, # interval to check execution of `update_records`
)
def update_records(records, ctx):
    # records get the records that adhere to the query
    for rec in records:
        # do something ,e.g., train a model, change records
        rec.metadata = {"updated": True}

    # ctx hold the listener info
    name = ctx.__listener__.dataset
    rg.log(name, records)
```

We can then start the listener by calling the function:

```python
update_records.start()
update_records.stop()
```

### Advanced

#### Conditional execution

We can set a condition for the expected number of records to require before actually executing the decorated function.

```python
@listener(
    dataset="my_dataset", # dataset to get record from
    condition=lambda search: search.total == 10, # only executes if `query` results in 10 records
)

@listener(
    dataset="my_dataset", # dataset to get record from
    condition=lambda search: search.total > 10, #  only executes if `query` results in more than 10 records
)
```

#### Updatable `query_params`

During an execution loop, it is possible to update and change `query_params` to allow for flexible querying based on the output of the query.

```python
@listener(
    dataset="uber-reviews", # dataset to get record from
    query="metadata.batch_id:{batch_id}",
    batch_id=0
)
def update_records(records, ctx):
    # next iteration the query is executed with batch_id = 1
    ctx.query_params["batch_id"] += 1
```

#### Metrics

Potentially actions like reporting can be done, based on the metrics provided by Argilla.

```python
@listener(
    dataset="my_dataset", # dataset to get record from
    metrics=["F1"]
)
def update_records(records, ctx):
    # next iteration the query is executed with batch_id = 1
    print(ctx.metrics)
```

#### Without loading records

Sometimes we might just want to listen without loading and processing the docs directly.

```python
@listener(
    dataset="my_dataset", # dataset to get record from
    query_records=False
)
def update_records(ctx):
    # Don`t load the records
    pass
```