Workspace
==========
This is the **entry point** to Rubrix. From this page, it is possible to open one or multiple datasets in order to work with them. 

Rubrix's Workspace is a **searchable and sortable list** of **datasets**, which contains the following attributes:

- **Search datasets bar**: this search bar allows users to search any keyword for finding a specific dataset, in case the list of datasets gets too long.
- **Name**: a column displaying the names of the loaded datasets. This column can be sorted alphabetically.
- **Tags**: a column which displays the ``tags`` passed to the ``rubrix.log`` method. These are useful to organize your datasets by project, model, status and any other dataset attribute you can think of.
- **Task**: this column is defined by the type of ``Records`` logged into the dataset (i.e. ``TextClassification`` or ``TokenClassification``).
- **Created at**: the timestamp of the dataset creation. Datasets in Rubrix are created by using ``rb.log``, for logging a collection of records.
- **Updated at**: the timestamp of the last update to this dataset (either by adding/changing/removing some annotations with the UI, via the Python client or via the REST API).
- **Sidebar**: 
   - **Refresh button**: allows updating the UI in order to display recent changes.
   - **List of workspaces**: allows the user to see the different workspaces they have to work with.

.. figure:: ../reference/webapp/webappui_images/workspace_1.png
   :alt: Rubrix Workspace view

   Rubrix Workspace view