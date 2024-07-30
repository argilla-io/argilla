---
description: In this section, we will provide a step-by-step guide for setting up Argilla in Hugging Face Spaces.
---

# Set up in Hugging Face Spaces

This guide explains how to deploy your Argilla app in a Hugging Face Space and configure it according to your preferences.

> For more information about Hugging Face Spaces, check the [documentation](https://huggingface.co/docs/hub/en/spaces-overview).


## Deploy Argilla on Spaces

1. Access the [Hugging Face template](https://huggingface.co/new-space?template=argilla/argilla-template-space). The template will show the Argilla Space SDK preselected.
2. Fill in the template. Take into account the following:

    -  Enable **Persistent Storage** not to lose your data. Unless you’re using a paid Space upgrade, any Space will be shut down after 48 hours of inactivity, resulting in data loss. You can do it later as detailed in ["Enable persistent storage"](#enable-persistent-storage), but all the data previous to the set up will be lost.
    -  Configure the **Space secrets** to manage the credentials. The default credentials and instructions for adding them later are described in ["Configure the Space secrets"](#configure-the-space-secrets).
    -  Set up the **visibility** to make your Space `public` or `private`. To access your private Space from the Argilla SDK, you will need to [configure and provide a `HF_TOKEN`](https://huggingface.co/settings/tokens)

3. Click "Create Space". The status will change to `Building` and, once it switches to `Running`, your Space will be ready. If you don't see the Argilla login UI, refresh the page.

!!! note "Argilla Space direct URL"

    The Argilla Space direct URL provides access to a full-screen, stable Argilla instance.

    It also serves as the `api_url` for reading and writing datasets using the Argilla SDK.

    This URL is constructed as follows: `https://[your-owner-name]-[your_space_name].hf.space`. For instance, if the owner of the Space is `argilla` and your Space name is `demo`, it will be `https://argilla-demo.hf.space`.


## Enable persistent storage

!!! warning
    Activate persistent storage not to loose your data. If you are not using a paid Space upgrade, any Space will be shut down after 48 hours of inactivity. When restarted, it will undergo a factory reset, resulting in the loss of all your data.

    Make sure to enable persistent storage before adding any data, as the Space will restart, removing all the previous data.

    If you haven’t enabled persistent storage, Argilla will display a warning message by default. To prevent this warning from appearing if you don’t need persistent storage, set the environment variable `ARGILLA_SHOW_HUGGINGFACE_SPACE_PERSISTENT_STORAGE_WARNING` to `false` in "Settings" > "New variable". This will suppress the warning message.

To enable [persistent storage](https://huggingface.co/docs/hub/spaces-storage#persistent-storage), go to the "Settings" tab on your created Space and click on the desired plan on the "Persistent Storage" section.

## Configure the Space secrets

[Secrets](https://huggingface.co/docs/hub/spaces-overview#managing-secrets) can be configured as optional settings to secure your Argilla Space.

The Argilla template allows you to configure the credentials for the default users: `owner`, `admin` and `annotator`. It will also allow you to configure the name of the default workspace.

> Check this [guide](../how_to_guides/user.md) to learn more about users, and refer to this [guide](../how_to_guides/workspace.md) for more information about workspaces in Argilla.

Moreover, it provides two secrets to configure the Hugging Face Oauth. For more information, check the [next section](#sign-in-with-hugging-face).

You can add the available secrets in "Settings" > "New secret".

??? note "Available secrets"

    | Secret name     | Type | Description | Default value   |
    |-------------------------------|----------|-------------|----------------|
    | `OWNER_USERNAME` | string | A username to log in with owner permissions | owner |
    | `OWNER_PASSWORD` | string | A password for the `OWNER_USERNAME` | 12345678 |
    | `OWNER_API_KEY` | string or online generator |An `api_key` to interact with the SDK with owner permissions | owner.apikey |
    | `ADMIN_USERNAME` | string |A username to log in with admin permissions | admin |
    | `ADMIN_PASSWORD` | string | A password for the `ADMIN_USERNAME` | 12345678 |
    | `ADMIN_API_KEY` | string or online generator|An `api_key` to interact with the SDK with admin permissions | admin.apikey |
    | `ANNOTATOR_USERNAME` | string |A username to log in with annotator permissions | argilla |
    | `ANNOTATOR_PASSWORD` | string |A password for the `ANNOTATOR_PASSWORD` | 12345678 |
    | `ARGILLA_WORKSPACE` | string | The name of the default workspace | admin |
    | `OAUTH2_HUGGINGFACE_CLIENT_ID` | ID | The Client ID of your connected app | |
    | `OAUTH2_HUGGINGFACE_CLIENT_SECRET` | ID | The app secret of your connected app | |


## Sign in with Hugging Face

The Hugging Face authentication allows you to give access to your Argilla Space to users that are logged in to the Hugging Face Hub.

!!! tip
    This feature is especially helpful for public crowdsourcing projects. The users logging in with OAuth will have the annotator role.

    To have more control over who can log in to the Space, you can set this up in a private Space so that only members of your organization can sign in.

    To create users with admin or owner roles, you can [create users](../how_to_guides/user.md) and access with their credentials.

!!! note
    If you duplicated an Argilla Space with OAuth instead of creating one from the template, make sure to also follow the next steps.

!!! warning
    If persistent storage is not enabled, make sure to activate the Hugging Face authentication before adding any data, as the Space will need to be restarted with a "Factory build", removing all the previous data.

1. [Create an OAuth App in Hugging Face](https://huggingface.co/settings/applications/new) and fill in the information:

    | Field        | Value |
    |--------------|----------|
    | Homepage URL | [`[Your Argilla Space direct URL]`](#deploy-argilla-on-spaces) |
    | Logo URL | `[Your Argilla Space direct URL]/favicon.ico` |
    | Scopes | `openid` and `profile` |
    | Redirect URL | `[Your Argilla Space Direct URL]/oauth/huggingface/callback`

2. Add the created Client ID and App Secret to your Space. It can be done in two different ways.

    === "As secrets"

        Add them to your Space in "Settings" > "New secret".

        | Secret name         | Value |
          |-------------------------------|----------|
          | `OAUTH2_HUGGINGFACE_CLIENT_ID` | [Your Client ID] |
          | `OAUTH2_HUGGINGFACE_CLIENT_SECRET` | [Your App Secret] |

    === "As environment variables in `.oauth.yaml`"

        Add them to your Space in "Files" > `.oauth.yaml`.

        !!! warning
            Be aware that the `.oauth.yaml` file is public in public spaces or may be accessible by other members of your organization in private spaces.

            Therefore, we recommend setting these variables as environment secrets.

        ??? quote "Example code in `.oauth.yaml`"
            ```yaml
            # This attribute will enable or disable the Hugging Face authentication
            enabled: true

            providers:
            # The OAuth provider setup
            # For now, only Hugging Face is supported
              - name: huggingface
                # This is the client ID of the OAuth app. You can find it in your Hugging Face settings.
                # see https://huggingface.co/docs/hub/oauth#creating-an-oauth-app for more info.
                # You can also provide it by using the env variable `OAUTH2_HUGGINGFACE_CLIENT_ID`
                client_id: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXXX

                # This is the client secret of the OAuth app. You can find it in your Hugging Face settings.
                # See https://huggingface.co/docs/hub/oauth#creating-an-oauth-app for more info.
                # We encourage you to provide it by using the env variable `OAUTH2_HUGGINGFACE_CLIENT_SECRET`
                client_secret: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXXX

                # The scope of the OAuth app. At least `openid` and `profile` are required.
                scope: openid profile

            # This section defines the allowed workspaces for the oauth users.
            # Workspaces defined here must exist in Argilla.
            allowed_workspaces:
                - name: admin
            ```

3. Check that the `enabled` parameter is set to `true` in "Files" > `.oauth.yaml`.
4. Go back to "Settings" and do a "Factory rebuild". Once the Space is restarted, you and your collaborators can sign and log in to your Space using their Hugging Face accounts.