# Filter a Feedback Dataset

From Argilla 1.15.0, the `filter_by` method has been included for the `FeedbackDataset`s pushed to Argilla, which allows you to filter the records in a dataset based on the `response_status` of the annotations of the records. So on, to be able to use the `filter_by` method, you will need to make sure that you are using a `FeedbackDataset` in Argilla.

## Filter by `response_status`

The `filter_by` method allows you to filter the records in a dataset based on the `response_status` of the annotations of the records. The `response_status` of an annotation can be one of the following: "draft", "missing", "discarded", or "submitted".

:::{note}
From Argilla 1.14.0, calling `from_argilla` will pull the `FeedbackDataset` from Argilla, but the instance will be remote, which implies that the additions, updates, and deletions of records will be pushed to Argilla as soon as they are made. This is a change from previous versions of Argilla, where you had to call `push_to_argilla` again to push the changes to Argilla.
:::

You can either filter the records by a single status or by a list of statuses. For example, to filter the records by the status "submitted", you can do the following:

```python
import argilla as rg

rg.init(api_url="<ARGILLA_API_URL>", api_key="<ARGILLA_API_KEY>")

dataset = rg.FeedbackDataset.from_argilla(name="my-dataset", workspace="my-workspace")
filtered_dataset = dataset.filter_by(response_status="submitted")
```

To filter the records by a list of statuses, you can do the following:

```python
import argilla as rg

rg.init(api_url="<ARGILLA_API_URL>", api_key="<ARGILLA_API_KEY>")

dataset = rg.FeedbackDataset.from_argilla(name="my-dataset", workspace="my-workspace")
filtered_dataset = dataset.filter_by(response_status=["submitted", "draft"])
```

:::{warning}
The `filter_by` method returns a new instance which is a `FeedbackDataset` with the filtered records and synced with Argilla, which means that you will just have access to the records that are compliant with the applied filter. So calling `filter_by` will return a `FeedbackDataset` with a subset of the records, but the records won't be modified unless updates or deletions are specifically applied at record-level. So on, the following methods are not allowed: `delete`, `delete_records`, `add_records`, `records.add`, and `records.delete`; while you'll still be able to perform record-level operations such as `update` or `delete`.
:::
