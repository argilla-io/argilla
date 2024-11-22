# SSO Integration Keycloak

## Set-up Keycloak

To test this run a test version of Keycloak in Docker:

```bash
docker run -p 8080:8080 -e KC_BOOTSTRAP_ADMIN_USERNAME=admin -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin quay.io/keycloak/keycloak:26.0.5 start-dev
```

General steps:
1. create a new realm and a new client to use with Argilla.
2. The client should expose the client audience via userinfo.
3. After that add the users you want to have access to argilla.

The script below should do all of that for you to test. It needs one python dependency you can install with `pip install python-keycloak`.


```python
from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenIDConnection
from keycloak import KeycloakOpenID

keycloak_connection = KeycloakOpenIDConnection(
    server_url="http://localhost:8080/",
    username="admin",
    password="admin",
    realm_name="master",
    client_id="admin-cli",
)

keycloak_admin = KeycloakAdmin(connection=keycloak_connection)

keycloak_admin.create_realm(
    {
        "realm": "argilla",
        "enabled": True,
        "displayName": "Argilla",
        "userManagedAccessAllowed": True,
    }
)
keycloak_connection = KeycloakOpenIDConnection(
    server_url="http://localhost:8080/",
    username="admin",
    password="admin",
    user_realm_name="master",
    realm_name="argilla",
)

keycloak_admin = KeycloakAdmin(connection=keycloak_connection)

client = keycloak_admin.create_client(
    {
        "clientId": "example-client",  # The client ID (you can choose a name)
        "enabled": True,
        "protocol": "openid-connect",  # Protocol (you can use other protocols like 'saml' if needed)
        "publicClient": False,  # Set to False if the client will use client secrets
        "directAccessGrantsEnabled": True,
        "standardFlowEnabled": True,
        "frontchannelLogout": True,
        "secret": "client-secret",  # Set a secret if it's not a public client
        "redirectUris": [
            "http://localhost:3000/*",
            "http://localhost:6900/*",
        ],  # Redirect URIs after authentication
    }
)

keycloak_openid = KeycloakOpenID(server_url="http://localhost:8080/",
                                 client_id="example-client",
                                 realm_name="argilla")

public_key = keycloak_openid.public_key()

client_scope = keycloak_admin.create_client_scope({
    "name": "example-client-scope_3",
    "protocol": "openid-connect"
})

# Create Audience Mapper
mapper = keycloak_admin.add_mapper_to_client_scope(
    client_scope_id=client_scope,
    payload={
    "name": "Client Audience",
    "protocol": "openid-connect",
    "protocolMapper": "oidc-audience-mapper",
    "consentRequired": False,
    "config": {
        "included.client.audience": "example-client",
        "id.token.claim": "false",
        "access.token.claim": "true"
    }
})

keycloak_admin.add_default_default_client_scope(client_scope)

new_user = keycloak_admin.create_user(
    {
        "email": "example@example.com",
        "username": "example",
        "enabled": True,
        "firstName": "Example",
        "lastName": "User",
        "credentials": [
            {
                "value": "secret",
                "type": "password",
            }
        ],
    }
)
```

## Set-up Argilla Server

After that you need to configure you endpoints in the `.oauth.yaml` same as this is done for the HuggingFace Oauth:

```yaml
# Change to `false` to disable HF oauth integration
#enabled: false

allow_http_redirect: true

providers:
  - name: keycloak
    client_id: <name of your client e.g. example-client>
    client_secret: <value of your specified secret e.g. client-secret>
    redirect_uri: http://localhost:3000/oauth/keycloak/callback # if you test locally
  - name: huggingface
    client_id: <create a new https://huggingface.co/settings/connected-applications>
    client_secret: <create a new https://huggingface.co/settings/connected-applications>
    redirect_uri: http://localhost:3000/oauth/huggingface/callback # if you test locally

# Allowed workspaces must exists
allowed_workspaces:
  - name: default
```

Then you need to set the two environment variables:

```bash
export SOCIAL_AUTH_KEYCLOAK_AUTHORIZATION_URL="http://localhost:8080/realms/argilla/protocol/openid-connect/auth"
export SOCIAL_AUTH_KEYCLOAK_ACCESS_TOKEN_URL="http://localhost:8080/realms/argilla/protocol/openid-connect/token"
export SOCIAL_AUTH_KEYCLOAK_PUBLIC_KEY=MIIBIj...
export SOCIAL_AUTH_KEYCLOAK_KEY=argilla
```

- `http://localhost:8080` is your keycloak endpoint in this case the local docker
- `argilla` is the name of the realm configured above
- `MIIBIj...` is the public key from the script above `public_key = keycloak_openid.public_key()`


