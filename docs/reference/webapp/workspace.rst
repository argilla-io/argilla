Workspace
==========
This is the **entry point** to Rubrix. From this page, it is possible to open one or multiple datasets.

Rubrix's Workspace is a **searchable and sortable list** of **datasets**, which contains the following attributes:


Search datasets bar
---------
The search bar allows users to search any keyword for finding a specific dataset (e.g., if the list of datasets gets too long).

Name
---------
A column displaying the names of the loaded datasets. This column can be sorted alphabetically.

Tags
---------
A column which displays the ``tags`` passed to the ``rubrix.log`` method.

These tags are useful to organize datasets by project, model, status and any other dataset attribute anyone can think of.

Task
---------
This column is defined by the type of ``Records`` logged into the dataset (i.e. ``TextClassification`` or ``TokenClassification``).

Created at
---------
This section represents the timestamp of the dataset creation. Datasets in Rubrix are created by using ``rb.log``, for logging a collection of records.

Updated at
---------
This section is the timestamp of the last update to a dataset (either by editing or removing annotations with the UI, via the Python client or via REST API).

Sidebar
---------
The sidebar consists of two parts:

   - **Refresh button**: allows updating the UI in order to display recent changes.
   - **List of workspaces**: allows the user to see the different workspaces they can work with.

.. image:: ../docs/reference/webapp/webappui_images/workspace_1.png
   :alt: Rubrix Workspace

   Rubrix Workspace
