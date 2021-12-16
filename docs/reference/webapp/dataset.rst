Dataset
==========
The **Dataset page** is the workspace for exploring and annotating records in a Rubrix dataset. Every task has its own specialized components, while keeping a similar layout and structure.

The search components and the two modes of operation (Explore and Annotation) are described below.

The Rubrix dataset page is driven by **search features**. The **search records bar** gives users quick filters for easily exploring and selecting data subsets.

The main sections of the search bar are following:

Search input
^^^^^^^^^^^^

This component enables:

1. **Full-text queries** over all record ``inputs``.

2. **Queries using Elasticsearch's query DSL** with the `query string syntax <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#query-string-syntax>`_\, which enables powerful queries for advanced users, using the Rubrix data model. Some examples are:
    -``inputs.text:(women AND feminists)`` : records containing the words "women" AND "feminist" in the inputs.text field.

    -``inputs.text:(NOT women)`` : records NOT containing women in the inputs.text field.

    -``inputs.hypothesis:(not OR don't)`` : records containing the word "not" or the phrase "don't" in the inputs.hypothesis field.

    -``metadata.format:pdf AND metadata.page_number>1`` : records with metadata.format equals pdf and with metadata.page_number greater than 1.

    -``NOT(_exists_:metadata.format)`` : records that don't have a value for metadata.format.

    -``predicted_as:(NOT Sports)`` : records which are not predicted with the label ``Sports``, this is useful when you have many target labels and want to exclude only some of them.

.. figure:: ../images/reference/ui/es_query_dsl_string.png
   :alt: Search input with Elasticsearch DSL query string

   Rubrix search input with Elasticsearch DSL query string


**NOTE**: Elasticsearch's query DSL supports **escaping special characters** that are part of the query syntax. The current list special characters are:

``+ - && || ! ( ) { } [ ] ^ " ~ * ? : \``

To escape these character use the \\ before the character. For example to search for (1+1):2 use the query:

``\(1\+1\)\:2``

Elasticsearch fields
^^^^^^^^^^^^^^^^^^^^

Shown below is a summary of available fields that can be used for the query DSL, as well as for building **Kibana Dashboards**— common fields to all record types, and those specific to certain record types:

+-----------------+
| Common fields   |
+=================+
| annotated_as    |
+-----------------+
| annotated_by    |
+-----------------+
| event_timestamp |
+-----------------+
| id              |
+-----------------+
| last_updated    |
+-----------------+
| metadata.*      |
+-----------------+
| multi_label     |
+-----------------+
| predicted       |
+-----------------+
| predicted_as    |
+-----------------+
| predicted_by    |
+-----------------+
| status          |
+-----------------+
| words           |
+-----------------+


+----------------------------+
| Text classification fields |
+============================+
| inputs.*                   |
+----------------------------+
| score                      |
+----------------------------+


+------------------------------+
| Tokens classification fields |
+==============================+
| tokens                       |
+------------------------------+



Predictions filters
^^^^^^^^^^^^^^^^^^^

This component allows filtering by aspects related to predictions, such as:

- **predicted as**: for filtering records by predicted labels,
- **predicted by**: for filtering by prediction_agent (e.g., different versions of a model),
- **predicted ok or ko**: for filtering records whose predictions are (or not) correct with respect to the annotations,
- **score**: for inspecting the score of a negative or positive label. Although this feature is displayed in all datasets, is only effective for results involving percentage or numbers (watch this, this or this tutorial to know more.)


Annotations filters
^^^^^^^^^^^^^^^^^^^

This component allows filtering by aspects related to annotations, such as:

- annotated as, for filtering records by annotated labels,
- annotated by, for filtering by annotation_agent (e.g., different human users or dataset versions)

.. figure:: ../images/reference/ui/annotation_filters.png
   :alt: Rubrix annotation filters

   Rubrix annotation filters

Status filter
^^^^^^^^^^^^^

This component allows filtering by record status:

- **Default**: records without any annotation or edition.
- **Validated**: records with validated annotations.
- **Edited**: records with annotations but not yet validated.

.. figure:: ../images/reference/ui/status_filters.png
   :alt: Rubrix status filters

   Rubrix status filters

Metadata filters
^^^^^^^^^^^^^^^^
This component allows filtering by metadata fields. The list of metadata categories is dynamic and it's created with the aggregations of metadata fields included in any of the logged records.

Sort filter
^^^^^^^^^^^^^^^^
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

Active query parameters
^^^^^^^^^^^^^^^^^^^^^^^
This component show the current active search parameters. It allows removing each individual param as well as all params at once.

.. figure:: ../images/reference/ui/active_query_params.png
   :alt: Active query params module

   Active query params module

Sidebar
^^^^^^^^^^^^^^^^^^^^^^^
TBD

Views
^^^^^^^^^^^^^^^^^^^^^^^
Dataset
==========
The **Dataset page** is the workspace for exploring and annotating records in a Rubrix dataset. Every task has its own specialized components, while keeping a similar layout and structure.

The search components and the two modes of operation (Explore and Annotation) are described below.

The Rubrix dataset page is driven by **search features**. The **search records bar** gives users quick filters for easily exploring and selecting data subsets.

The main sections of the search bar are following:

Search input
^^^^^^^^^^^^

This component enables:

1. **Full-text queries** over all record ``inputs``.

2. **Queries using Elasticsearch's query DSL** with the `query string syntax <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#query-string-syntax>`_\, which enables powerful queries for advanced users, using the Rubrix data model. Some examples are:
    -``inputs.text:(women AND feminists)`` : records containing the words "women" AND "feminist" in the inputs.text field.

    -``inputs.text:(NOT women)`` : records NOT containing women in the inputs.text field.

    -``inputs.hypothesis:(not OR don't)`` : records containing the word "not" or the phrase "don't" in the inputs.hypothesis field.

    -``metadata.format:pdf AND metadata.page_number>1`` : records with metadata.format equals pdf and with metadata.page_number greater than 1.

    -``NOT(_exists_:metadata.format)`` : records that don't have a value for metadata.format.

    -``predicted_as:(NOT Sports)`` : records which are not predicted with the label ``Sports``, this is useful when you have many target labels and want to exclude only some of them.

.. figure:: ../images/reference/ui/es_query_dsl_string.png
   :alt: Search input with Elasticsearch DSL query string

   Rubrix search input with Elasticsearch DSL query string


**NOTE**: Elasticsearch's query DSL supports **escaping special characters** that are part of the query syntax. The current list special characters are:

``+ - && || ! ( ) { } [ ] ^ " ~ * ? : \``

To escape these character use the \\ before the character. For example to search for (1+1):2 use the query:

``\(1\+1\)\:2``

Elasticsearch fields
^^^^^^^^^^^^^^^^^^^^

Shown below is a summary of available fields that can be used for the query DSL, as well as for building **Kibana Dashboards**— common fields to all record types, and those specific to certain record types:

+-----------------+
| Common fields   |
+=================+
| annotated_as    |
+-----------------+
| annotated_by    |
+-----------------+
| event_timestamp |
+-----------------+
| id              |
+-----------------+
| last_updated    |
+-----------------+
| metadata.*      |
+-----------------+
| multi_label     |
+-----------------+
| predicted       |
+-----------------+
| predicted_as    |
+-----------------+
| predicted_by    |
+-----------------+
| status          |
+-----------------+
| words           |
+-----------------+


+----------------------------+
| Text classification fields |
+============================+
| inputs.*                   |
+----------------------------+
| score                      |
+----------------------------+


+------------------------------+
| Tokens classification fields |
+==============================+
| tokens                       |
+------------------------------+



Predictions filters
^^^^^^^^^^^^^^^^^^^

This component allows filtering by aspects related to predictions, such as:

- **predicted as**: for filtering records by predicted labels,
- **predicted by**: for filtering by prediction_agent (e.g., different versions of a model),
- **predicted ok or ko**: for filtering records whose predictions are (or not) correct with respect to the annotations,
- **score**: for inspecting the score of a negative or positive label. Although this feature is displayed in all datasets, is only effective for results involving percentage or numbers (watch this, this or this tutorial to know more.)


Annotations filters
^^^^^^^^^^^^^^^^^^^

This component allows filtering by aspects related to annotations, such as:

- annotated as, for filtering records by annotated labels,
- annotated by, for filtering by annotation_agent (e.g., different human users or dataset versions)

.. figure:: ../images/reference/ui/annotation_filters.png
   :alt: Rubrix annotation filters

   Rubrix annotation filters

Status filter
^^^^^^^^^^^^^

This component allows filtering by record status:

- **Default**: records without any annotation or edition.
- **Validated**: records with validated annotations.
- **Edited**: records with annotations but not yet validated.

.. figure:: ../images/reference/ui/status_filters.png
   :alt: Rubrix status filters

   Rubrix status filters

Metadata filters
^^^^^^^^^^^^^^^^
This component allows filtering by metadata fields. The list of metadata categories is dynamic and it's created with the aggregations of metadata fields included in any of the logged records.

Sort filter
^^^^^^^^^^^^^^^^
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

Active query parameters
^^^^^^^^^^^^^^^^^^^^^^^
This component show the current active search parameters. It allows removing each individual param as well as all params at once.

.. figure:: ../images/reference/ui/active_query_params.png
   :alt: Active query params module

   Active query params module

Sidebar
^^^^^^^^^^^^^^^^^^^^^^^
TBD- MORE TO ADD

The sidebar consists of the following submenus:

- **Refresh button**:
- **Progress**: with this submenu, it is possible to check how much has been annotated, validated and discarded. The labels record can also be checked here.
- **Stats**: this submenu displays the keywords and information such as the error distribution. It can change depending on the task performed.

Views
^^^^^^^^^^^^^^^^^^^^^^^
TBD- MORE TO ADD

There are three different views, all available for users_:

- **Annotation View**,
- **Explore View**,
- **Rules (Filter) View**