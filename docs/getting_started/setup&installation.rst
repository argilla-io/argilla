.. _setup-and-installation:

Setup and installation
======================

In this guide, we will help you to get up and running with Rubrix. Basically, you need to:

1. Install the Python client
2. Launch the web app

1. Install the Rubrix Python client
------------------------------------

First, make sure you have Python 3.6 or above installed.

Then you can install Rubrix with ``pip``\ :

.. code-block:: bash

   pip install rubrix

2. Setup and launch the webapp
------------------------------

There are two ways to launch the webapp:

#. Using `docker-compose <https://docs.docker.com/compose/>`_ (**recommended**).
#. Executing the server code manually

Using ``docker-compose`` (recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For this method you first need to install `Docker Compose <https://docs.docker.com/compose/install/>`_.

Then, create a folder:

.. code-block:: bash

   mkdir rubrix && cd rubrix

and launch the docker-contained web app with the following command:

.. code-block:: bash

   wget -O docker-compose.yml https://raw.githubusercontent.com/recognai/rubrix/master/docker-compose.yaml && docker-compose up

This is the recommended way because it automatically includes an
`Elasticsearch <https://www.elastic.co/elasticsearch/>`_ instance, Rubrix's main persistent layer.

Executing the server code manually
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When executing the server code manually you need to provide an
`Elasticsearch <https://www.elastic.co/elasticsearch/>`_ instance yourself.
This method may be preferred if you (1) want to avoid or cannot use ``Docker``,
(2) have an existing Elasticsearch service, or
(3) want to have full control over your Elasticsearch configuration.

1. First you need to install
   `Elasticsearch <https://www.elastic.co/guide/en/elasticsearch/reference/7.10/install-elasticsearch.html>`_
   (we recommend version 7.10) and launch an Elasticsearch instance.
   For MacOS and Windows there are
   `Homebrew formulae <https://www.elastic.co/guide/en/elasticsearch/reference/7.13/brew.html>`_ and a
   `msi package <https://www.elastic.co/guide/en/elasticsearch/reference/current/windows.html>`_, respectively.
2. Install the Rubrix Python library together with its server dependencies:

.. code-block:: bash

   pip install rubrix[server]

3. Launch a local instance of the Rubrix web app

.. code-block::

   python -m rubrix.server

By default, the Rubrix server will look for your Elasticsearch endpoint at ``http://localhost:9200``.
If you want to customize this, you can set the ``ELASTICSEARCH`` environment variable pointing to your endpoint.

Checking your webapp and REST API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now you should be able to access Rubrix via `http://localhost:6900/ <http://localhost:6900/>`_\ ,
and you can also check the API docs at `http://localhost:6900/api/docs <http://localhost:6900/api/docs>`_.

3. Testing the installation by logging some data
------------------------------------------------

The following code will log one record into a data set called ``example-dataset`` :

.. code-block:: python

   import rubrix as rb

   rb.log(
       rb.TextClassificationRecord(inputs={"text": "my first rubrix example"}),
       name='example-dataset'
   )

You should receive this response in your terminal or Jupyter Notebook:

.. code-block:: bash

   BulkResponse(dataset='example-dataset', processed=1, failed=0)

This means that the data has been logged correctly.

If you now go to your Rubrix app at `http://localhost:6900/ <http://localhost:6900/>`_ , you will find your first data set.

Congratulations! You are ready to start working with Rubrix.

Next steps
----------

To continue learning we recommend you to:


* Check our **guides** and **tutorials.**
* Read about Rubrix's main **concepts.**
