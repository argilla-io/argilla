# User Roles

This guide gathers all the relevant information about the type of users available at Argilla.

A user is an authorized person who can access the UI and use the Python client and CLI in a running Argilla instance. We differentiate between three types of users depending on their role, permissions and needs: `owner`, `admin`, `annotator`.

## Owner

The owner is the **root user** who created the Argilla instance. When working with Argilla, it is very useful to work with workspaces. So, the owner has full access to all workspaces and their options:

- **Workspace management**: It can create and delete a workspace.
- **User management**: It can create a new user, update its information, assign a workspace to a user, and delete a user. It can also list all of them and search for a specific user by its name or ID.
- **Dataset management**: It can create, configure, update, and delete datasets. It can also delete the current FeedbackDataset from Argilla.
- **Annotation**: It can annotate datasets in the Argilla UI.
- **Feedback**: It can provide feedback with the Argilla UI.


## Admin

An admin user can only access the workspaces it has been assigned to and cannot assign other users to it. An admin user has the following permissions:

- **Dataset management**: It can create, configure, update, and delete datasets (including FeedbackDataset) only on assigned workspaces.
- **Annotation**: It can annotate datasets in the assigned workspaces via the Argilla UI.
- **Feedback**: It can provide feedback with the Argilla UI.


## Annotator

Annotator users are limited to accessing only the datasets assigned to them within the workspace. They have two specific permissions:

- **Annotation**: It can annotate datasets in the Argilla UI.
- **Feedback**: It can provide feedback with the Argilla UI.


## More information

For more information, you can refer to the following links:

 - [User management](https://docs.argilla.io/en/latest/getting_started/installation/configurations/user_management.html)
 - [Workspace management](https://docs.argilla.io/en/latest/getting_started/installation/configurations/workspace_management.html)