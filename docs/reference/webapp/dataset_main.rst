Dataset
==========
The main sections of the search bar are following:

- **Record cards**
    - Text classification
        - Single label
        - Multi label
    - Token classification
    - Text2Text
-  **Search bar**
    - Active query parameters
- **Filters**
    - Predictions
    - Annotations
    - Status
    - Metadata 
    - Sort 
- **Sidebar**
    - Modes/Views
        - Explore
        - Annotate
        - Define rules
    - Metrics
        - Progress
        - Stats
        - Refresh

The **Dataset page** is the workspace for exploring and annotating records in a Rubrix dataset. Every task has its own specialized components, while keeping a similar layout and structure.

The search components and the two modes of operation (Explore and Annotation) are described below.

The Rubrix dataset page is driven by **search features**. The **search records bar** gives users quick filters for easily exploring and selecting data subsets.

Record cards
---------
TBD

Search bar
---------
This section is available `here <searchbar.rst>`_\.

**ACTIVE QUERY PARAMETERS**
This component show the current active search parameters. It allows removing each individual param as well as all params at once.

.. figure:: ../images/reference/ui/active_query_params.png
   :alt: Active query params module

   Active query params module

Filters
---------
**PREDICTION FILTERS**

This component allows filtering by aspects related to predictions, such as:

- **predicted as**: for filtering records by predicted labels,
- **predicted by**: for filtering by prediction_agent (e.g., different versions of a model),
- **predicted ok or ko**: for filtering records whose predictions are (or not) correct with respect to the annotations,
- **score**: for inspecting the score of a negative or positive label. Although this feature is displayed in all datasets, is only effective for results involving percentage or numbers (watch this, this or this tutorial to know more.)

With the exception of the score filter, which works in a different way, several filters can be chosen in the different sections.

Here is an example of how the score can work for a text classification task:

**ANNOTATION FILTERS**

This component allows filtering by aspects related to annotations. This can be very useful when it comes to handle a lot of data.

The different filters are the following:

- **annotated as**: for filtering records by annotated labels. Several labels can be selected, and if an user creates a new one, it will be shown on the drop down.
- **annotated by**: for filtering by annotation_agent (e.g., different human users or dataset versions). This agent can be established when programming ``Records``. 

.. figure:: ../images/reference/ui/annotation_filters.png
   :alt: Rubrix annotation filters

   Rubrix annotation filters

**STATUS FILTER**

This component allows filtering by record status:

- **Default**: records without any annotation or edition.
- **Validated**: records with validated annotations.
- **Edited**: records with annotations but not yet validated.

.. figure:: ../images/reference/ui/status_filters.png
   :alt: Rubrix status filters

   Rubrix status filters

**METADATA FILTERS**
This component allows filtering by metadata fields. 

The list of **metadata categories** is dynamic and it's created with the aggregation of metadata fields included in any of the logged records.

Several filters can be chosen in order to see different metadata, and it will display a result of records with the same metadata category.

**SORT FILTERS**
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
TBD