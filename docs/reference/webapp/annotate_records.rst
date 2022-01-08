Annotate Records
^^^^^^^^^^^^^^^^^^^
In terms of annotating records, the **Annotation mode** enables users to add and modify annotations. This mode follows the same interaction patterns as in the `Explore mode <explore_records.rst>`_\  (e.g., using filters and advanced search).

The `Define rules mode <define_labelingrules.rst>`_\ works slightly different, even though its features can be seen in its `section <define_labelingrules.rst>`_\.

Novel features, such as **bulk annotation** for a given set of search parameters are also available.

When it comes to annotate records, the interface can be divided in three parts:

- **How to annotate**,
- **Filter and search**
- and **Sidebar and metrics**

More detailed information about these features can be found `here <dataset_main.rst>`_\. This section will explain the actions related to annotation.

How to annotate
---------
This section is intended to explain how the **Annotation Mode** works.

When choosing this mode, the display of the dataset is slightly different. The **"Bulk Annotation"** bar appears (see below), and records appear editable.

Users can annotate one by one, or several records in a row, but the annotation will change depending on the task:

Text2Text Tasks
~~~~~~~~~~

On **text2text tasks**, records can be edited, validated or discarded.


Token Classification Tasks
~~~~~~~~~~

On **token classification tasks**, the record will show different labels on its words (tokens). Users can pick words or sequences of words in order to annotate them with labels, and then, records can be validated or discarded.


Text Classification Tasks
~~~~~~~~~~

On **text classification tasks**, a record will be displayed with different labels below. Users have to choose one or more labels (or validate the selected one) and validate the record. Records can be discarded too.

.. figure:: ../_static/images/webappui_images/random_examples.mp4

Bulk Annotation
---------
With this feature, from 5 to 20 records can be validated or discarded at the same time, depending on how many records per page are being displayed.

In order to use it, users must operate with the bar placed below the search bar and the filters. One or more records can be selected by clicking on specific checkbox or choosing the "Select all" checkbox.

After choosing the records to be annotated, a label must be selected on the "Annotate as" dropdown, and after that, these records must be validated or discarded.

It is also posible to create new labels for any classification task (tokenization, text classification...).

Filters and search
---------
Using filters can be very helpful when it comes to annotate specific records or to carry out subtasks (this often happens when datasets are big).

More information about these features can be found  `here <dataset_main.rst>`_\, and their use is described  `here <filter_records.rst>`_\.

With respect to searching records, more information can be found `here <search_records.rst>`_\.

Sidebar and metrics
---------
In all modes (**Explore**, **Annotation** and **Define rules**), the **Metrics** menu is available on the sidebar. Learn more about it  `here <dataset_main.rst>`_\  (features) or  `here <metrics.rst>`_\  (an "user guide").

.. figure:: ../_static/images/webappui_images/annotation_textcat.png
   :alt: Rubrix Text Classification Annotation mode

   Rubrix Text Classification Annotation mode


.. figure:: ../_static/images/webappui_images/annotation_ner.png
   :alt: Rubrix Token Classification (NER) Annotation mode

   Rubrix Token Classification (NER) Annotation mode

Annotation by different users will be saved with different annotation agents.
To setup various users in your Rubrix server, please refer to our `user management guide <https://docs.rubrix.ml/en/stable/getting_started/user-management.html>`_.

Click `here <https://docs.rubrix.ml/en/stable/getting_started/setup%26installation.html>`_\  to start with the installation or the first tutorial (a list with different tutorials is available).
