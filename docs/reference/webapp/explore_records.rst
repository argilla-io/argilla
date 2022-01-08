Explore Records
^^^^^^^^^^^^^^^^^^^
The **Exploration mode** turns out convenient when it comes to explore and analyze records in a dataset. 

As Rubrix allows different tasks to be carried out `(more information here <workspace.rst>)`_\, different visualizations are tailored for the task. For example, it is possible to see and analyze the keywords, metrics, the labels and to choose the parameters described above. 

When it comes to explore records, the interface can be divided in three parts:

- **Search records**,
- **Records**, 
- and **Sidebar**

More detailed information about these features can be found `here <dataset_main.rst>`_\. This section will explain the actions that are related to exploring records.

Tasks and Records
---------
As it is known, Rubrix deals with three different types of tasks: **Text2Text**, **Token Classification** and **Text Classification**.

- **Text2Text Tasks**: in these tasks, where the model receives and outputs a sequence of tokens, the main objective is to display arranged records. Thus, it is possible to use the Metrics menu (on the sidebar) and to analyze the score, the prediction agent and the status, or users can also sort the results by these parameters.

In order to gain further knowledge of the aforementioned aspects, read the section devoted to `datasets <dataset_main.rst>`_\.

- **Token Classification Tasks**: as tokenization gives a lot of importance to words (tokens), the way they are labeled is key in these tasks. 
   
   When it comes to explore records for tokenization tasks, Rubrix displays labels in a very transparent way— each label in a dataset has a different color, and their caption is displayed next to the search bar. In addition to this, all filters can be used to analyze the records, as well as the Metrics menu.

- **Text Classification Tasks**: the **Exploration Mode** works in a very similar way to token classification tasks. The filters and menus are the same, but in this case this mode is very interesting with binary models— when it comes to positive or negative annotations, their corresponding icon is displayed next to the record.

.. figure:: ../images/reference/ui/explore_textcat.png
   :alt: Rubrix Text Classification Explore mode

   Rubrix Text Classification Explore mode

An example is displayed here:

.. figure:: ../images/reference/ui/explore_ner.png
   :alt: Rubrix Token Classification (NER) Explore mode

   Rubrix Token Classification (NER) Explore mode