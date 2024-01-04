# 🗂️ Assign records to your team

Depending on the nature of your project and the size of your annotation team, you may want to have control over annotation overlap i.e., having multiple annotations for a single record. In this section, we'll demonstrate an easy way to accomplish this.


## Feedback Dataset

```{include} /_common/feedback_dataset.md
```

### Full overlap

The Feedback Task supports having multiple annotations for your records by default. This means that all users with access to the dataset can give responses to all the records in the dataset. To have this full overlap just push the dataset (as detailed in [Create a Feedback Dataset](create_dataset.md#push-to-argilla)) in a workspace where all team members have access. Learn more about managing user access to workspaces [here](/getting_started/installation/configurations/user_management.md#assign-a-user-to-a-workspace).

### Controlled overlap

We provide easy-to-use utility functions for distributing records among your team. Below, we outline a general approach for this task. For a more comprehensive example, please refer to our end-to-end tutorials.

1. Get the list of users who will be annotating and the records.

```python
import argilla as rg

# Optional: filter users to get only those with annotator role
users = [u for u in rg.User.list() if u.role == "annotator"]

records = [...]
```

2. Use the `assign_records` function to assign the annotations. You can specify the assignment parameters by providing the following arguments:

 - `users`: The list of users or the dictionary with groups and the corresponding users. This will allow you to make the assignments among users or groups of users.
 - `records`: The list of records.
 - `overlap`: The number of annotations per record. Take in mind that a group will be treated as a unique annotator and all the members of the same group will annotate the same records.
 - `shuffle`: Whether to shuffle the records before assigning them. Defaults to `True`.

```python
from argilla.client.feedback.utils import assign_records
assignments = assign_records(
    users=users,
    records=records,
    overlap=1,
    shuffle=True
)
```

3. Assign the records by pushing a dataset to their corresponding workspaces. For this, you can use `assign_workspaces` that will check if there exists the workspace or create it if needed. You can specify the parameters by providing the following arguments:

- `assignments`: The dictionary with the assignments from the previous step.
- `workspace_type`: Either `group`, `group_personal` or `individual`. Selecting `group` means each group shares a workspace and annotates the same dataset. If you choose `group_personal`, every group member gets a personal workspace. Use `individual` when you are not working with groups (i.e., a list of individual users), where each user will have a separate workspace.

```python
from argilla.client.feedback.utils import assign_workspaces

assignments = assign_workspaces(
    assignments=assignments,
    workspace_type="individual"
)

for username, records in assignments.items():
    dataset = rg.FeedbackDataset(
        fields=fields,
        questions=questions,
        metadata_properties=metadata_properties,
        vector_settings=vector_settings,
        guidelines=guidelines
    )
    dataset.add_records(records)
    remote_dataset = dataset.push_to_argilla(name="my_dataset", workspace=username)
```

```{Note}
If you prefer to have a single dataset accessible to all teammates, you can assign the records using the metadata whether without overlap (by adding a single annotator as metadata to each record) or with overlap (by adding a list of multiple annotators). Annotators will just need to filter the dataset in the Argilla UI by their username to get their assigned records:
```python
#Add the metadata to the existing records using id to identify each record
id_modified_records = {}
for username, records in assignments.items():
    for record in records:
        record_id = id(record)
        if record_id not in id_modified_records:
            id_modified_records[record_id] = record
            record.metadata["annotators"] = []
        if username not in id_modified_records[record_id].metadata["annotators"]:
            id_modified_records[record_id].metadata["annotators"].append(username)

# Get the unique records with their updated metadata
modified_records = list(id_modified_records.values())

# Push the dataset with the modified records
dataset = rg.FeedbackDataset(
        fields=fields,
        questions=questions,
        metadata_properties=[rg.TermsMetadataProperty(name="annotators")]
        vector_settings=vector_settings,
        guidelines=guidelines,
    )
dataset.add_records(modified_records)
remote_dataset = dataset.push_to_argilla(name="my_dataset", workspace="workspace_name")
```


## Other datasets

```{include} /_common/other_datasets.md
```

### Zero overlap
By default these datasets don't allow overlap i.e., they only allow one response. This means that you only need to log your dataset in a workspace where all members of the annotation team have access to get zero overlap.

You may ask your team to self-organize and work on any available invalidate records but to avoid stepping on each other's toes, it is recommended to divide the records among your teammates. Follow [this tutorial](/getting_started/installation/configurations/workspace_management) to learn how.


### Full overlap
If you would like to collect responses from all members of your annotation team for every record, then you will need to log the full dataset several times, once in each annotator's personal workspace.

To do this, get a list of users as explained [above](#id1) and run the following code:

```python
# Make a list of records
records = [...]

# Loop through the user list
for user in users:
    # Check that the user has a personal workspace and create it if not
    try:
        workspace = rg.Workspace.from_name(user.username)
    except:
        workspace = rg.Workspace.create(user.username)
        user = rg.User.from_name(user.username)
        workspace.add_user(user.id)

    # Log the records in their personal workspace
    rg.log(
        records=records,
        workspace=workspace,
        name='my_dataset'
    )
```

### Controlled overlap
To control the annotation overlap in these datasets you can follow the same method detailed in [the section about Feedback Datasets](#controlled-overlap), although with a different logging method. Once you have run the code in that section to make the assignments, you can log them like so:

```python
# Loop through the assignments dictionary
for user, records in assignments.items():
    # Check that the user has a personal workspace and create it if not
    try:
        workspace = rg.Workspace.from_name(user.username)
    except:
        workspace = rg.Workspace.create(user.username)
        user = rg.User.from_name(user.username)
        workspace.add_user(user.id)
    # Log the records in their personal workspace
    rg.log(
        records=records,
        workspace=workspace,
        name="my_dataset"
    )
```
