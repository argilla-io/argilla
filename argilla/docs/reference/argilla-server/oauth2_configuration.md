# OAuth2 configuration

Argilla supports OAuth2 authentication for users. This allows users to authenticate using other services like Google,
GitHub, or Hugging Face. Next sections will guide you through the configuration of the OAuth2 authentication.

## The OAuth2 configuration file

The OAuth2 configuration file is a YAML file that contains the configuration for the OAuth2 providers that you want to
enable. The default file name is `.oauth.yml` and it should be placed in the root directory of the Argilla server. You
can also specify a different file name using the `ARGILLA_AUTH_OAUTH_CFG` environment variable.

The file should have the following structure:

```yaml
providers:
  - name: huggingface
    client_id: "<client_id>"
    client_secret: "<client_secret>"
    scope: "openid profile"

  - name: google-oauth2
    client_id: "<client_id>"
    client_secret: "<client_secret>"
    scope: "openid email profile"

  - name: github
    client_id: "<client_id>"
    client_secret: "<client_secret>"

allowed_workspaces:
  - name: argilla

allow_http_redirect: false
```

### Providers

The `providers` key is a list of dictionaries, each dictionary represents a provider configuration, including the following fields:

- `name`: The name of the provider. The available options by default are `huggingface`, `github` and `google-oauth2`. We will see later how to add more providers not supported by default.
- `client_id`: The client ID provided by the OAuth2 provider. You can get this value by creating an application in the provider's developer console. This is a required field, but you can also use the `ARGILLA_OAUTH2_<PROVIDER_NAME>_CLIENT_ID` environment variable to set the value.
- `client_secret`: The client secret provided by the OAuth2 provider. You can get this value by creating an application in the provider's developer console. This is a required field, but you can also use the `ARGILLA_OAUTH2_<PROVIDER_NAME>_CLIENT_SECRET` environment variable to set the value.
- `scope`: The scope of the OAuth2 provider. This is an optional field, and normally you don't need to set it, but you can use it to request specific permissions from the user access.

### Allowed Workspaces

The `allowed_workspaces` key is a list of dictionaries, each dictionary represents a workspace configuration. For now, only the `name` field is defined, and it should be the name of the workspace that the user will be assigned to when logging in.
If the workspace doesn't exist, it will be created automatically on the first server startup.

### Allow HTTP Redirect

The `allow_http_redirect` key is a boolean value that allows the OAuth2 provider to redirect the user to an HTTP URL. By default, this value is set to `false`, and you should set it to `true` only if you are running the Argilla server behind a proxy that doesn't support HTTPS or if you are running the server locally.
Enabling this option is not recommended for production environments and should be used only for development purposes.

## Supported OAuth2 providers configuration

The following sections will guide you through the configuration of the supported OAuth2 providers. Before diving into the configuration, you should create an application in the provider's developer console to get the client ID and client secret.

A common step when creating an application in the provider's developer console is to set the redirect URI. The redirect URI is the URL where the OAuth2 provider will redirect the user after the authentication process.
The redirect URI should be set to the Argilla server URL, followed by `/oauth/<provider_name>/callback`. For example, if the Argilla server is running on `http://localhost:8000`, the redirect URI for provider application should be `http://localhost:8000/oauth/huggingface/callback`.

##  Hugging Face OAuth2 configuration

Argilla supports Hugging Face OAuth2 authentication out of the box, and is already configured when running Argilla on Hugging Face Spaces (See the [Hugging Face Spaces settings](../../getting_started/how-to-configure-argilla-on-huggingface.md) for more information).

But, if you want to manually configure the Hugging Face OAuth2 provider, you should define the following fields in the `.oauth.yml` file:

```yaml

providers:
  - name: huggingface
    client_id: "<client_id>" # You can use the ARGILLA_OAUTH2_HUGGINGFACE_CLIENT_ID environment variable
    client_secret: "<client_secret>" # You can use the ARGILLA_OAUTH2_HUGGINGFACE_CLIENT_SECRET environment variable
    scope: "openid profile" # This field is optional. But this value must be aligned your OAuth2 application created in Hugging Face.

allowed_workspaces:
    - name: argilla
```

To get your client ID and client secret, you need to create an [OAuth2 application](https://huggingface.co/settings/applications/new) in the Hugging Face settings page.

The minimal scope required for the Hugging Face OAuth2 provider is `openid profile`, so you don't need to change the `scope` when creating the application.

## GitHub OAuth2 configuration

Argilla also supports GitHub OAuth2 authentication out of the box. To configure the GitHub OAuth2 provider, you should define the following fields in the `.oauth.yml` file:

```yaml

providers:
  - name: github
    client_id: "<client_id>" # You can use the ARGILLA_OAUTH2_GITHUB_CLIENT_ID environment variable
    client_secret: "<client_secret>" # You can use the ARGILLA_OAUTH2_GITHUB_CLIENT_SECRET environment variable

...
```

To get your client ID and client secret, you need to register a new [OAuth application](https://github.com/settings/applications/new) in the GitHub settings page.

## Google OAuth2 configuration

Argilla also supports Google OAuth2 authentication out of the box. To configure the Google OAuth2 provider, you should define the following fields in the `.oauth.yml` file:

```yaml

providers:
  - name: google-oauth2
    client_id: "<client_id>" # You can use the ARGILLA_OAUTH2_GOOGLE_OAUTH2_CLIENT_ID environment variable
    client_secret: "<client_secret>" # You can use the ARGILLA_OAUTH2_GOOGLE_OAUTH2_CLIENT_SECRET environment variable

...
```

To get your client ID and client secret, you need to create a new [OAuth2 client](https://console.cloud.google.com/apis/credentials/oauthclient) in the Google Cloud Console.

## Adding more OAuth2 providers

If you want to add more OAuth2 providers that are not supported by default, you can do so by adding a new provider configuration to the `.oauth.yml` file.
The Argilla server uses the [Social Auth backends](https://python-social-auth.readthedocs.io/en/latest/backends/index.html) component to define the provider configuration. You only need to register the provider backend using the `extra_backends` key in the `.oauth.yml` file.

For example, to configure the [Apple OAuth2 provider](https://python-social-auth.readthedocs.io/en/latest/backends/apple.html), you should add the following configuration to the `.oauth.yml` file:

```yaml

providers:
  - name: apple-id
    client_id: "<client_id>" # You can use the ARGILLA_OAUTH2_APPLE_ID_CLIENT_ID environment variable
    client_secret: "<client_secret>" # You can use the ARGILLA_OAUTH2_APPLE_ID_CLIENT_SECRET environment variable

extra_backends:
    - social_core.backends.apple.AppleIdAuth # Register the Apple OAuth2 provider backend

```
All the `SOCIAL_AUTH_* environment variables are supported by the Argilla server, so you can customize the provider configuration using these environment variables.

