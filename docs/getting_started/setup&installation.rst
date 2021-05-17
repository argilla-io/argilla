.. _setup-and-installation:

Setup and installation
======================

In this guide, we will help you to get up and running with Rubrix. Basically, you need to:


#. Setup and launch the webapp, whose main external dependency is `Elasticsearch <https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html#install-elasticsearch>`_\ , Rubrix's main persistence layer.
#. Install the Python library.

1. Setup and launch the webapp
------------------------------

There are two ways of launching the webapp:


#. Using **Docker** and a ``docker-compose`` file we provide with all you need for the *webapp* (recommended).
#. Setting up your own Elasticsearch installation and launching the Rubrix server. This method is useful if you (1) want to avoid or cannot use ``Docker``\ , (2)  have an existing Elasticsearch service, or (3) want to have full control over your Elasticsearch configuration.

Using Docker and ``docker-compose`` (recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You first need to install the `Docker Engine <https://docs.docker.com/engine/install/>`_ for your platform.

You can launch your docker-contained environment with the following command:

.. code-block:: bash

   wget -O docker-compose.yml https://raw.githubusercontent.com/recognai/rubrix/master/docker-compose.yaml && docker-compose up

Using an Elasticsearch installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


#. If you do not have an existing Elasticsearch installation,  install `Elasticsearch <https://www.elastic.co/guide/en/elasticsearch/reference/7.12/install-elasticsearch.html>`_ and launch your Elasticsearch instance.
#. Install the Rubrix Python library following the `guide <>`_ below.
#. Launch a local instance of the Rubrix webapp ``python -m rubrix.server``. By default, the Rubrix server will look for your ES endpoint URL at ``http://localhost:9200`` if you want to customize this, you can setup the ``ELASTICSEARCH`` env variable with your ES endpoint URL.

Checking your webapp and REST API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You should be able to access Rubrix via `http://localhost:6900/ <http://localhost:6900/>`_\ , and you can also check the API docs at `http://localhost:6900/api/docs <http://localhost:6900/api/docs>`_.

2. Install the Rubrix Python library
------------------------------------

First, make sure you have Python 3.6-3.8 and ``pip`` installed. 

Before installing the library  recommend you to create a fresh `Conda virtual environment <https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html>`_\ ,  `venv <https://docs.python.org/3/library/venv.html>`_ or a similar virtual environment manager.

Then you can install Rubrix with ``pip``\ :

.. code-block:: bash

   pip install rubrix

3. Testing the installation by logging some data
------------------------------------------------

The following code will log one record into the ``example-dataset`` :

.. code-block:: python

   import rubrix as rb

   rb.log(
       rb.TextClassificationRecord(inputs={"text": "my first rubrix example"}),
       name='example-dataset'
   )

You should receive this response in your terminal or your Jupyter Notebook:

.. code-block:: bash

   BulkResponse(dataset='example-dataset', processed=1, failed=0)

Which means that the data has been logged correctly. 

If you go to your Rubrix app at `http://localhost:6900/ <http://localhost:6900/>`_\ , you will find your first dataset.

Congratulations! You are ready to start working with Rubrix with your own data. 

Next steps
----------

To continue learning we recommend you to:


* Check our **guides** and **tutorials.**
* Read about Rubrix's main **concepts.**
