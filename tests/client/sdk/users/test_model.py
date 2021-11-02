from rubrix.client.sdk.users.models import User
from rubrix.server.security.model import User as ServerUser


def test_users_schema(helpers):
    client_schema = User.schema()
    server_schema = ServerUser.schema()

    assert helpers.remove_description(client_schema) == helpers.remove_description(
        server_schema
    )
