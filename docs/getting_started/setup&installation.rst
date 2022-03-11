.. _setup-and-installation:

Setup and installation
======================

In this guide, we will help you to get up and running with Rubrix.
Basically, you need to:

1. Install Rubrix
2. Launch the web app
3. Start logging data

1. Install Rubrix
-----------------

First, make sure you have Python 3.7 or above installed.

Then you can install Rubrix with ``pip`` or ``conda``\.

**with pip**

.. code-block:: bash

   pip install rubrix[server]==0.12.1

**with conda**

.. code-block:: bash

   conda install -c conda-forge rubrix-server


2. Launch the web app
---------------------

Rubrix uses `Elasticsearch (ES) <https://www.elastic.co/elasticsearch/>`__ as its main persistent layer.
**If you do not have an ES instance running on your machine**, we recommend setting one up :ref:`via docker <setting-up-elasticsearch-via-docker>`.

You can start the Rubrix web app via Python.

.. code-block:: bash

   python -m rubrix

Afterward, you should be able to access the web app at `http://localhost:6900/ <http://localhost:6900/>`__.
**The default username and password are** ``rubrix`` **and** ``1234`` (see the `user management guide <user-management.ipynb>`_ to configure this).

Have a look at our :ref:`advanced setup guides <advanced-setup-guides>` if you want to (among other things):

- :ref:`configure the Rubrix server <server-configurations>`
- :ref:`share an ES instance with other applications <configure-elasticsearch-role-users>`
- :ref:`deploy Rubrix on an AWS instance <deploy-to-aws-instance-using-docker-machine>`

.. note::
   You can also launch the web app via :ref:`docker <launching-the-web-app-via-docker>` or :ref:`docker-compose <launching-the-web-app-via-docker-compose>`.
   For the latter you do not need a running ES instance.

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

**Congratulations! You are ready to start working with Rubrix.**

Next steps
----------

To continue learning we recommend you to:

* Check our **Guides** and **Tutorials.**
* Read about Rubrix's main :ref:`concepts`
