.. _setup-and-installation:

Setup and installation
======================

In this guide, we will help you to get up and running with Rubrix. Basically, you need to:

1. Install the Python client
2. Launch the web app
3. Start logging data

1. Install the Rubrix Python client
------------------------------------

First, make sure you have Python 3.6 or above installed.

Then you can install Rubrix with ``pip``\ :

.. code-block:: bash

   pip install rubrix==0.5.0

2. Launch the web app
---------------------

There are two ways to launch the webapp:

a. Using `docker-compose <https://docs.docker.com/compose/>`__ (**recommended**).
b. Executing the server code manually

a) Using ``docker-compose`` (recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For this method you first need to install `Docker Compose <https://docs.docker.com/compose/install/>`__.

Then, create a folder:

.. code-block:: bash

   mkdir rubrix && cd rubrix

and launch the docker-contained web app with the following command:

.. code-block:: bash

   wget -O docker-compose.yml https://raw.githubusercontent.com/recognai/rubrix/master/docker-compose.yaml && docker-compose up

This is the recommended way because it automatically includes an
`Elasticsearch <https://www.elastic.co/elasticsearch/>`__ instance, Rubrix's main persistent layer.

b) Executing the server code manually
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When executing the server code manually you need to provide an
`Elasticsearch <https://www.elastic.co/elasticsearch/>`__ instance yourself.
This method may be preferred if you
(1) want to avoid or cannot use ``Docker``,
(2) have an existing Elasticsearch service, or
(3) want to have full control over your Elasticsearch configuration.

1. First you need to install
   `Elasticsearch <https://www.elastic.co/guide/en/elasticsearch/reference/7.10/install-elasticsearch.html>`__
   (we recommend version 7.10) and launch an Elasticsearch instance.
   For MacOS and Windows there are
   `Homebrew formulae <https://www.elastic.co/guide/en/elasticsearch/reference/7.13/brew.html>`__ and a
   `msi package <https://www.elastic.co/guide/en/elasticsearch/reference/current/windows.html>`__, respectively.

2. Install the Rubrix Python library together with its server dependencies:

.. code-block:: bash

   pip install rubrix[server]==0.5.0

3. Launch a local instance of the Rubrix web app

.. code-block::

   python -m rubrix.server

By default, the Rubrix server will look for your Elasticsearch endpoint at ``http://localhost:9200``.
But you can customize this by setting the ``ELASTICSEARCH`` environment variable.

**If you are already running an Elasticsearch instance for other applications and want to share it with Rubrix**, please refer to our :ref:`advanced setup guide <configure-elasticsearch-role-users>`.

3. Start logging data
---------------------

The following code will log one record into a data set called ``example-dataset`` :

.. code-block:: python

   import rubrix as rb

   rb.log(
       rb.TextClassificationRecord(inputs="My first Rubrix example"),
       name='example-dataset'
   )

If you now go to your Rubrix app at `http://localhost:6900/ <http://localhost:6900/>`__ , you will find your first data set.
**The default username and password are** ``rubrix`` **and** ``1234`` (see the :ref:`user management guide <user-management>` to configure this).
You can also check the REST API docs at `http://localhost:6900/api/docs <http://localhost:6900/api/docs>`__.

Congratulations! You are ready to start working with Rubrix.

Please refer to our :ref:`advanced setup guides <advanced-setup-guides>` if you want to:

- setup Rubrix using docker
- share the Elasticsearch instance with other applications
- deploy Rubrix on an AWS instance
- manage users in Rubrix

.. **If you want to setup Rubrix using docker, share the Elasticsearch instance with other applications,  or manage users in the Rubrix server**, please refer to our :ref:`advanced setup guides <advanced-setup-guides>`.

Next steps
----------

To continue learning we recommend you to:

* Check our **Guides** and **Tutorials.**
* Read about Rubrix's main :ref:`concepts`



