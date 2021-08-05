.. role:: raw-html-m2r(raw)
   :format: html


Setup and Installation in cloud providers
=========================================

Download
--------

.. code-block:: shell

   docker pull recognai/rubrix:v0.1.3

Launch (external elasticsearch)
-------------------------------

.. code-block:: shell

   docker run -p 6900:6900 -e "ELASTICSEARCH=<your-elasticsearch-instance-url>" --name rubrix recognai/rubrix:v0.1.3

Find running instance
---------------------

.. code-block:: shell

   docker ps

Stop container
--------------

.. code-block:: shell

   docker stop rubrix

Deploy your own elasticsearch cluster
-------------------------------------

Follow the docker installation guide on the `official elasticsearch page <https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html>`_

Configure elasticsearch role/users
----------------------------------

If you have an Elasticsearch instance and want to share resources with other applications, you can easily configure it for using Rubrix.

All you need to take into account is:


* 
  Rubrix will create its ES indices with the following pattern ``.rubrix_*``. It's recommended to create a new role (e.g., rubrix) and provide it with all privileges for this index pattern.

* 
  Rubrix creates an index template for these indices, so you may provide related template privileges to this ES role.

Rubrix uses the ``ELASTICSEARCH`` environment variable to set the ES connection. 

You can provide the credentials using the following scheme: 

.. code-block:: bash

      http(s)://user:passwd@elastichost

.. code-block:: python

      http(s)://user:passwd@elastichost...

Below you can see a screenshot for setting up a new ``rubrix`` Role and its permissions:

:raw-html-m2r:`<img src="https://user-images.githubusercontent.com/15624271/123934452-40e26000-d9ce-11eb-967d-a46a0b2afa1f.png"/>`

Deploy to aws instance using docker-machine
-------------------------------------------

Setup an AWS profile
^^^^^^^^^^^^^^^^^^^^

The ``aws`` command cli must be installed. Then, type:

.. code-block:: shell

   aws configure --profile rubrix

and follow command instructions. For more details, visit `AWS official documentation <https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html>`_

Once the profile is created (a new entry should be appear in file ``~/.aws/config``\ ), you can activate it via setting environment variable:

.. code-block:: shell

   export AWS_PROFILE=rubrix

Create docker machine (aws)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

   docker-machine create --driver amazonec2 \
   --amazonec2-root-size 60 \
   --amazonec2-instance-type t2.large \
   --amazonec2-open-port 80 \
   --amazonec2-ami ami-0b541372 \
   --amazonec2-region eu-west-1 \
   rubrix-aws

Available ami depends on region. The provided ami is available for eu-west regions

Verify machine creation
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

   $>docker-machine ls

   NAME                   ACTIVE   DRIVER      STATE     URL                        SWARM   DOCKER     ERRORS
   rubrix-aws             -        amazonec2   Running   tcp://52.213.178.33:2376           v20.10.7

Save asigned machine ip
^^^^^^^^^^^^^^^^^^^^^^^

In our case, the assigned ip is ``52.213.178.33``

Connect to remote docker machine
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To enable the connection between the local docker client and the remote daemon, we must type following command:

.. code-block:: shell

   eval $(docker-machine env rubrix-aws)

Define a docker-compose.yaml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   # docker-compose.yaml
   version: "3"

   services:
     rubrix:
       image: recognai/rubrix:v0.1.3
       ports:
         - "80:80"
       environment:
         ELASTICSEARCH: <elasticsearch-host_and_port>
       restart: unless-stopped

Pull image
^^^^^^^^^^

.. code-block:: shell

   docker-compose pull

 Launch docker container
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

   docker-compose up -d

Accessing to rubrix
^^^^^^^^^^^^^^^^^^^

In our case http://52.213.178.33
