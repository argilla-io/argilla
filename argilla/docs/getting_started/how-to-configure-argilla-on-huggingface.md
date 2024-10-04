---
description: Configure Argilla on Hugging Face Spaces
title: Hugging Face Spaces Settings
---

This section details how to configure and deploy Argilla on Hugging Face Spaces. It covers:

- Persistent storage
- How to deploy Argilla under a Hugging Face Organization
- How to configure and disable HF OAuth access
- How to use Private Spaces

!!! tip "Looking to get started easily?"
    If you just discovered Argilla and want to get started quickly, go to the [Quickstart guide](quickstart.md).

## Persistent storage

In the Space creation UI, persistent storage is set to `Small PAID`, which is a paid service, charged per hour of usage.

**Spaces get restarted due to maintainance, inactivity, and every time you change your Spaces settings**. Persistent storage enables Argilla to save to disk your datasets and configurations across restarts.

!!! warning "Ephimeral FREE persistent storage"
    Not setting persistent storage to `Small` means that **you will loose your data when the Space restarts**.

    If you plan to **use the Argilla Space beyond testing**, it's highly recommended to **set persistent storage to `Small`**.

If you just want to quickly test or use Argilla for a few hours with the risk of loosing your datasets, choose `Ephemeral FREE`. `Ephemeral FREE` means your datasets and configuration will not be saved to disk, when the Space is restarted your datasets, workspaces, and users will be lost.

If you want to disable the persistence storage warning, you can set the environment variable `ARGILLA_SHOW_HUGGINGFACE_SPACE_PERSISTENT_STORAGE_WARNING=false`

!!! warning "Read this if you have datasets and want to enable persistent storage"
    If you want to enable persistent storage `Small PAID` and you have created datasets, users, or workspaces, follow this process:

    - First, **make a local or remote copy of your datasets**, following the [Import and Export guide](../how_to_guides/import_export.md). This is the most important step, because changing the settings of your Space leads to a restart and thus a data loss.
    - If you have created users (not signed in with Hugging Face login), **consider storing a copy of users** following the [manage users guide](../how_to_guides/user.md).
    - **Once you have stored all your data safely, go to you Space Settings Tab** and select `Small`.
    - **Your Space will be restarted and existing data will be lost**. From now on, all the new data you create in Argilla will be kept safely
    - **Recover your data**, by following the above mentioned guides.

## How to configure and disable OAuth access

By default, Argilla Spaces are configured with Hugging Face OAuth, in the following way:

- Any Hugging Face user that can see your Space, can use the Sign in button, join as an `annotator`, and contribute to the datasets available under the `argilla` workspace. This workspace is created during the deployment process.
- These users can only explore and annotate datasets in the `argilla` workspace but can't perform any critical operation like create, delete, update, or configure datasets. By default, any other workspace you create, won't be visible to these users.

To restrict access or change the default behaviour, there's two options:

**Set your Space to private**. This is especially useful if your Space is under an organization. This will **only allow members within your organization to see and join your Argilla space**. It can also be used for personal, solo projects.

**Modify the `.oauth.yml` configuration file**. You can find and modify this file under the `Files` tab of your Space. The default file looks like this:

```yaml
# Change to `false` to disable HF oauth integration
#enabled: false

providers:
  - name: huggingface

# Allowed workspaces must exists
allowed_workspaces:
  - name: argilla
```
You can modify two things:

- Uncomment `enabled: false` to completely disable the Sign in with Hugging Face. If you disable it make sure to set the `USERNAME` and `PASSWORD` Space secrets to be able to login as an `owner`.
- Change the list of `allowed` workspaces.

For example if you want to let users join a new workspace `community-initiative`:

```yaml
allowed_workspaces:
  - name: argilla
  - name: community-initiative
```

## How to deploy Argilla under a Hugging Face Organization

Creating an Argilla Space within an organization is useful for several scenarios:

- **You want to only enable members of your organization to join your Space**. You can achieve this by setting your Space to private.
- **You want manage the Space together with other users** (e.g., Space settings, etc.). Note that if you just want to manage your Argilla datasets, workspaces, you can achieve this by adding other Argilla `owner` roles to your Argilla Server.
- **More generally, you want to make available your space under an organization/community umbrella**.

The steps are very similar the [Quickstart guide](quickstart.md) with one important difference:

!!! tip "Enable Persistent Storage `SMALL`"
    Not setting persistent storage to `Small` means that **you will loose your data when the Space restarts**.

    For Argilla Spaces with many users, it's strongly recommended to **set persistent storage to `Small`**.

## How to use Private Spaces

Setting your Space visibility to private can be useful if:

- You want to work on your personal, solo project.
- You want your Argilla to be available only to members of the organization where you deploy the Argilla Space.

You can set the visibility of the Space during the Space creation process or afterwards under the `Settings` Tab.

To use the Python SDK with private Spaces you need to specify your `HF_TOKEN` which can be found [here](https://huggingface.co/settings/tokens), when creating the client:

```python
import argilla as rg

HF_TOKEN = "..."

client = rg.Argilla(
    api_url="<api_url>",
    api_key="<api_key>"
    headers={"Authorization": f"Bearer {HF_TOKEN}"}
)
```


## Space Secrets overview

There's two optional secrets to set up the `USERNAME` and `PASSWORD` of the `owner` of the Argilla Space. Remember that, by default Argilla Spaces are configured with a *Sign in with Hugging Face* button, which is also used to grant an `owner` to the creator of the Space for personal spaces.

The `USERNAME` and `PASSWORD` are only useful when you want to create a specific user to login into Argilla, if not your user account will we granted the `owner` role after the login with OAuth.
