.. _python_client:

Client
======

Here we describe the Python client of Argilla that we divide into four basic modules:

- :ref:`python ref methods`: These methods make up the interface to interact with Argilla's REST API.
- :ref:`python ref records`: You need to wrap your data in these *Records* for Argilla to understand it.
- :ref:`python ref datasets`: Datasets: You can wrap your records around these *Datasets* for extra functionality.
- :ref:`python ref feedbackdataset`: FeedbackDataset: the dataset format for *FeedbackTask* and LLM support.


.. _python ref methods:

Methods
-------

.. automodule:: argilla
   :members: init, log, load, copy, delete, set_workspace, get_workspace, delete_records, active_client

.. _python ref records:

Records
-------

.. automodule:: argilla.client.models
   :members:
   :exclude-members: BaseRecord, BulkResponse

.. _python ref datasets:

Datasets
--------

.. automodule:: argilla.client.datasets
   :members: DatasetForTextClassification, DatasetForTokenClassification, DatasetForText2Text, read_datasets, read_pandas

.. _python ref feedbackdataset:

FeedbackDataset
---------------

.. automodule:: argilla.client.feedback.dataset
   :members: FeedbackDataset

.. automodule:: argilla.client.feedback.schemas
   :members: FeedbackDatasetConfig, RatingQuestion, TextQuestion, LabelQuestion, MultiLabelQuestion, QuestionSchema, TextField, FieldSchema, FeedbackRecord
