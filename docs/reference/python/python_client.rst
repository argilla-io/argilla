.. _python_client:

Client
======

Here we describe the Python client of Rubrix that we divide into three basic modules:

- :ref:`python ref methods`: These methods make up the interface to interact with Rubrix's REST API.
- :ref:`python ref records`: You need to wrap your data in these *Records* for Rubrix to understand it.
- :ref:`python ref datasets`: Datasets: You can wrap your records around these *Datasets* for extra functionality.

.. _python ref methods:

Methods
-------

.. automodule:: rubrix
   :members: init, log, load, copy, delete, set_workspace, get_workspace, delete_records

.. _python ref records:

Records
-------

.. automodule:: rubrix.client.models
   :members:
   :exclude-members: BaseRecord, BulkResponse

.. _python ref datasets:

Datasets
--------

.. automodule:: rubrix.client.datasets
   :members: DatasetForTextClassification, DatasetForTokenClassification, DatasetForText2Text, read_datasets, read_pandas
