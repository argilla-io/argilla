.. _python_client:

Client
======

Here we describe the Python client of Rubrix that we divide into two basic modules:

- Methods: These methods make up the interface to interact with Rubrix's REST API.
- Models: You need to wrap your data in these data models for Rubrix to understand it.

Methods
-------

.. automodule:: rubrix
   :members:

Models
------

.. automodule:: rubrix.client.models
   :members:
   :exclude-members: BaseRecord, BulkResponse

Datasets
--------

.. automodule:: rubrix.client.datasets
   :members: DatasetForTextClassification, DatasetForTokenClassification, DatasetForText2Text, read_datasets, read_pandas
