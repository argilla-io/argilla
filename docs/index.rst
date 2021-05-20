.. rubrix documentation master file, created by
   sphinx-quickstart on Fri Mar 26 17:19:26 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


First steps with Rubrix
=======================

What's Rubrix?
--------------

`Rubrix <https://rubrix.ml>`_ is a free and open-source tool for tracking and iterating on data for AI projects. 

With Rubrix, you can:


* **Monitor** the predictions of deployed models.
* **Collect** ground-truth data for starting up a project or evolving an existing one.
* **Iterate** on ground-truth data and predictions to debug, track and improve your models over time.
* **Build** custom applications and dashboards on top of your model predictions and ground-truth data.

Rubrix is designed to enable novel, human-in-the loop workflows involving data scientists, subject matter experts and data engineers for curating, understanding and evolving data for AI projects.

We've tried to make Rubrix easy, fun and seamless to use with your favourite libraries while keeping it scalable and flexible. Rubrix's main components are:


* a **Python library**  you can install with ``pip`` to interact with your data and models,
* a **web application and a REST API,** you can launch using ``Docker`` or with a local installation.


.. image:: images/rubrix_intro.svg
   :alt: images/rubrix_intro.svg


Rubrix's architecture and components

Rubrix currently focuses on ``natural language processing`` and ``knowledge graph`` use cases but we will be adding support for speech recognition and computer vision soon. 

Quickstart
----------

Getting started with the Rubrix is really easy, let's see a quick example using the 🤗 ``transformers`` and ``datasets`` libraries:


#. 
   Make sure you have ``Docker`` installed and run (check our **Setup and Installation[add_link]** guide for a more detailed installation process):
   
   .. code-block::

      wget -O docker-compose.yml https://raw.githubusercontent.com/recognai/rubrix/master/docker-compose.yaml && docker-compose up


   #. Install Rubrix python library (and ``transformers`` and ``datasets`` libraries for this example):

``pip install rubrix transformers datatasets``


#. Use your favourite editor or a Jupyter notebook to run the following:

Text classification deals with predicting in which categories a text fits. As if you're shown an image you could quickly tell if there's a dog or a cat in it, we build NLP models to distinguish between a Jane Austen's novel or a Charlotte Bronte's poem. It's all about feeding models with labeled examples and see how it start predicting over the very same labels.

.. code-block:: python

   from transformers import pipeline
   from datasets import load_dataset  
   import rubrix as rb

   model = pipeline('zero-shot-classification', model="typeform/squeezebert-mnli")

   dataset = load_dataset("ag_news", split='test[0:100]')

   for record in dataset:
       # Our labels are: ['World', 'Sports', 'Business', 'Sci/Tech']
       prediction = model(record['text'], dataset.features["label"].names) 

       item = rb.TextClassificationRecord(
           inputs={"text": record["text"]},
           prediction=list(zip(prediction['labels'], prediction['scores'])), 
           annotation=categories[record["label"]]
       )

       rb.log(item, name="ag_news_zeroshot")

.. raw:: html

   <iframe width="100%" height="500" src="https://www.youtube.com/embed/9s87bb2UMdA?autoplay=1" frameborder="0" allowfullscreen allow='autoplay'></iframe>

Use cases
---------

* **Model monitoring and observability:** log and observe predictions of live models.
* **Ground-truth data collection**: collect labels to start a project from scratch or from existing live models.
* **Evaluation**: easily compute "live" metrics from models in production, and slice evaluation datasets to test your system under specific conditions.
* **Model debugging**: log predictions during the development process to visually spot issues.
* **Explainability:** log things like token attributions to understand your model predictions.
* **App development:** get a powerful search-based API on top of your model predictions and ground truth data.

Design Principles
-----------------

Rubrix design is:

* **Agnostic**: you can use Rubrix with any library or framework, no need to implement any interface or modify your existing toolbox and workflows.
* **Flexible:**  Rubrix does not make any strong assumption about your input data, so you can log and structure your data as it fits your use case.
* **Minimalistic:** Rubrix is built around a small set of concepts and methods.

Next steps
----------

The documentation is divided in different categories, which explore each aspect and use case of Rubrix. Here you have quick links to each one:

* :ref:`setup-and-installation`
* :ref:`concepts`
* **Tutorials**
* **Guides**
* **Reference**

Community
---------
You can join the conversation on our Github page and our Github forum.

* `Github page <https://github.com/recognai/rubrix>`_
* `Github forum <https://github.com/recognai/rubrix/discussions>`_


.. toctree::
   :maxdepth: 3
   :caption: Getting Started
   :hidden:

   self
   getting_started/setup&installation
   getting_started/concepts
   getting_started/supported_tasks

.. toctree::
   :maxdepth: 3
   :caption: Guides
   :hidden:

   guides/streamlit_guide.rst
   
.. toctree::
   :maxdepth: 3
   :caption: Tutorials
   :hidden:

   tutorials/01-huggingface
   tutorials/02.spacy
   tutorials/03-kglab_pytorch_geometric

.. toctree::
   :maxdepth: 3
   :caption: Reference
   :hidden:

   reference/python_client_api

.. toctree::
   :maxdepth: 2
   :caption: Community
   :hidden:

   Github page <https://github.com/recognai/rubrix>
   Discussion forum <https://github.com/recognai/rubrix/discussions>

