Dataset
==========

The **Dataset page** is the workspace for exploring and annotating records in a Rubrix dataset. Every task has its own specialized components, while keeping a similar layout and structure.

The search components and the two modes of operation (`Explore <explore_records.rst>`_\ and `Annotation <annotate_records.rst>`_\) are described below.

Rubrix dataset page is driven by **search features**. The **search records bar** gives users quick filters for easily exploring and selecting data subsets.

The main sections of the search bar are following:

.. toctree::

Record cards
Search bar
Filters
Sidebar

Record cards
---------
There are three different types of record cards in Rubrix:

Text classification
~~~~~~~~~~
This type of record deals with predicting in which categories a text fits. This records usually deals with  multilabel text classification, sentiment analysis, semantic similarity, stance detection, and much more.

In this case, these records can be **single** or **multilabel**— this means, that there are records with different number of labels, where one or more can be selected.

Token classification
~~~~~~~~~~
This type of record is intended to divide the input text into words, or syllables, and assign certain values to them. It is specially useful for NER tasks, POS tagging or any task more focused on Lingustics.

Text2Text
~~~~~~~~~~
The expression Text2Text encompasses text generation tasks where the model receives and outputs a sequence of tokens. Examples of such tasks are machine translation, text summarization, paraphrase generation, etc.

These three types of cards are composed by the same components described below, although their modes differ. These are the links for reading about the `Annotation Mode <annotate_records.rst>`_\ and about the `Exploration Mode <explore_records.rst>`_\.

Search bar
---------
This section is available `here <searchbar.rst>`_\.

Active query parameters
~~~~~~~~~~

This component show the current active search parameters. It allows removing each individual param as well as all params at once.

.. figure:: ../images/reference/ui/active_query_params.png
   :alt: Active query params module

   Active query params module

Filters
---------
Prediction filters
~~~~~~~~~~

This component allows filtering by aspects related to predictions, such as:

- **predicted as**: for filtering records by predicted labels,
- **predicted by**: for filtering by prediction_agent (e.g., different versions of a model),
- **predicted ok or ko**: for filtering records whose predictions are (or not) correct with respect to the annotations,
- **score**: for inspecting the score of a negative or positive label. Although this feature is displayed in all datasets, is only effective for results involving percentage or numbers (watch this, this or this tutorial to know more.)

With the exception of the score filter, which works in a different way, several filters can be chosen in the different sections.

Here is an example of how the score can work for a text classification task:

Annotation filters
~~~~~~~~~~

This component allows filtering by aspects related to annotations. This can be very useful when it comes to handle a lot of data.

The different filters are the following:

- **annotated as**: for filtering records by annotated labels. Several labels can be selected, and if an user creates a new one, it will be shown on the drop down.
- **annotated by**: for filtering by annotation_agent (e.g., different human users or dataset versions). This agent can be established when programming ``Records``. 

.. figure:: ../images/reference/ui/annotation_filters.png
   :alt: Rubrix annotation filters

   Rubrix annotation filters

Status filter
~~~~~~~~~~

This component allows filtering by record status:

- **Default**: records without any annotation or edition.
- **Validated**: records with validated annotations.
- **Edited**: records with annotations but not yet validated.

.. figure:: ../images/reference/ui/status_filters.png
   :alt: Rubrix status filters

   Rubrix status filters

Metadata filter
~~~~~~~~~~

This component allows filtering by metadata fields. 

The list of **metadata categories** is dynamic and it's created by aggregating metadata fields, included in any of the logged records.

Several filters can be chosen in order to see different metadata, and it will display a result of records with the same metadata category.

Sort filter
~~~~~~~~~~

With this component, users are able to sort the information on the dataset by the following parameters:
    - Predicted as,
    - Predicted ok,
    - Score,
    - Predicted by,
    - Annotated as,
    - Annotated by,
    - Status,
    - Metadata.category/loss/topic/- (this one is not available in every dataset).

Please, note that these parameters could change depending on the kind of dataset used and the tasks to be performed.

Sidebar
---------
Modes
~~~~~~~~~~
Rubrix has three modes available:

- **Explore mode**: learn more `here <explore_records.rst>`_\.
- **Annotate mode**: learn more `here <annotate_records.rst>`_\.
- **Define rules mode**: learn more `here <define_labelingrules.rst`_\.

Metrics
~~~~~~~~~~
This component allow users to check the statistics, progress, error distribution and keywords of a dataset.

It is composed by two submenus and the **Refresh** button:

- **Progress**: this submenu allows tracking how many records are annotated, validated and/or discarded. 
- **Stats**: this submenu allows users to know more about the keywords and the error distribution of the dataset. 
- **Refresh**: with this button, it is possible to update the dataset page, in order to see changes applied.

