# Set up your annotation team
Depending on the nature of your project and the size of your annotation team, you may want to have control over annotation overlap i.e., having multiple annotations for a single record. In this section, we will demonstrate 3 different workflows to get the level of overlap you need: full, zero or controlled.

```{note}
You will need to decide the level of overlap before creating or pushing a dataset to Argilla, as this has implications on how your dataset is set up.
```

## Full overlap

The Feedback Task supports having multiple annotations for your records by default. This means that all users with access to the dataset can give responses to all the records in the dataset. To have this full overlap just push the dataset (as detailed in [Create a Feedback Dataset](create_dataset.md#push-to-argilla)) in a workspace where all team members have access. Learn more about managing user access to workspaces [here](../../../getting_started/installation/configurations/user_management.md#assign-a-user-to-a-workspace).

## Zero overlap
If you only want one annotation per record, we recommend that you split your records into chunks and assign each of them to a single annotator. Then, you can create several datasets, one in each annotator's personal workspace with the records assigned to them.

```{note}
This assumes that each annotator has a personal workspace attached to their user. If this is not the case, learn how create a workspace and assign it to a user [here](../../../getting_started/installation/configurations/user_management.md#assign-a-user-to-a-workspace).
```

Here's how you can do this:

1. Get the list of users who will be annotating:

```python
import argilla as rg

rg.init(
    api_url="...",
    api_key="..."
)

# get the list of users
# optional: filter users to get only those with annotator role
users = [u for u in rg.User.list() if u.role == "annotator"]
```

```{note}
If you are using a version earlier than 1.11.0 you will need to call the API directly to get the list of users. Note that, in that case, users will be returned as dictionaries and so `users.username` will be `users['username']` instead.
```python
# make a request using your Argilla Client to get the list of users
rg_client= rg.active_client().client
auth_headers = {"X-Argilla-API-Key": rg_client.token}
http=httpx.Client(base_url=rg_client.base_url, headers=auth_headers)
users = http.get("/api/users").json()

# filter users to get only those with annotator role
users = [user for user in users if user["role"]=="annotator"]
```

2. Get a list of the records that each will annotate:

```python
import random
from collections import defaultdict

records = [...] # A Python list containing all the records in your dataset

# optional: shuffle the records to get a random assignment
random.shuffle(records)

# build a dictionary where the key is the username and the value is the list of records assigned to them
assignments = defaultdict(list)

# divide your records in chunks of the same length as the users list and make the assignments
# you will need to follow the instructions to create and push a dataset for each of the key-value pairs in this dictionary
n = len(users)
chunked_records = [records[i:i + n] for i in range(0, len(records), n)]
for chunk in chunked_records:
    for idx, record in enumerate(chunk):
        assignments[users[idx].username].append(record)
```

3. Loop through the dictionary of assignments to create one dataset per user:

```{note}
If you haven't done so already, decide on the settings of the project (the `fields`, `questions` and `guidelines`) as detailed in the [Create a Feedback Dataset guide](create_dataset.ipynb) and set them as variables.
```

```python
fields = [...]
questions = [...]
guidelines = "..."

for username, records in assignments.items():
    # check that the user has a personal workspace and create it if not
    try:
        workspace = rg.Workspace.from_name(username)
    except:
        workspace = rg.Workspace.create(username)
        user = rg.User.from_name(username)
        workspace.add_user(user.id)

    # create a dataset with their assingment and push to their workspace
    ds = rg.FeedbackDataset(fields=fields, questions=questions, guidelines=guidelines)
    ds.add_records(records)
    ds.push_to_argilla(name="my_dataset", workspace=workspace.name)
```

```{note}
The `Workspace` class was introduced in Argilla's Python SDK in version 1.11.0. To manage and create workspaces in earlier versions of Argilla check our [User Management Guide](../../../getting_started/installation/configurations/user_management.md)
```

## Controlled overlap
Sometimes you prefer to have more control over the annotation overlap and decide on a limited number of responses you want for each record. You may opt for this option because you want your team to be more efficient or perhaps to calculate the agreement between pairs of annotators. In this case, you also need to create several datasets and push them to the annotators' personal workspaces with the difference that each record will appear in multiple datasets.

For this method, follow the same steps as in the [zero overlap](#zero-overlap) solution, substituting the second step with the following code:

```python
import random

# code to assign with predetermined overlap
def assign_records(users, records, overlap):
    assignments = {user.username: [] for user in users}
    random.shuffle(records)

    num_users = len(users)
    num_records = len(records)
    num_assignments = num_records * overlap

    assignments_per_user = num_assignments // num_users

    for i in range(num_records):
        record = records[i]

        for j in range(overlap):
            user_index = (i * overlap + j) % num_users
            user = users[user_index].username
            assignments[user].append(record)

    return assignments

assignments = assign_records(users, records, overlap=3)
```

Like in the previous method, you will need to import the assignment of each annotator as a separate dataset in their personal workspace, as demonstrated in the step no.3. On post-processing, you can combine the responses to each record.

```{warning}
If you use this method, we recommend you will need to add an id to the records in order to combine the responses in post-processing. Learn how to set a record id [here](create_dataset.md#add-records).
```
