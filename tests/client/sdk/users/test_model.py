from rubrix.client.sdk.users.models import User
from rubrix.server.security.model import User as ServerUser


def test_users_schema(helpers):
    client_schema = User.schema()
    server_schema = ServerUser.schema()

    for clean_method in [helpers.remove_description, helpers.remove_pattern]:
        client_schema = clean_method(client_schema)
        server_schema = clean_method(server_schema)

    assert client_schema == server_schema
