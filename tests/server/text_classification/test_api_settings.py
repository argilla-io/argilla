import rubrix as rb
from rubrix.server.apis.v0.models.commons.model import TaskType


def create_dataset(client, name: str):
    response = client.post(
        "/api/datasets/", json={"name": name, "task": TaskType.text_classification}
    )
    assert response.status_code == 200


def test_create_dataset_settings(mocked_client):
    name = "test_create_dataset_settings"
    rb.delete(name)
    create_dataset(mocked_client, name)

    response = create_settings(mocked_client, name)
    assert response.status_code == 200

    created = response.json()
    response = fetch_settings(mocked_client, name)
    assert response.json() == created


def create_settings(mocked_client, name):
    response = mocked_client.put(
        f"/api/datasets/{TaskType.text_classification}/{name}/settings",
        json={"labels_schema": {"labels": ["Label1", "Label2"]}},
    )
    return response


def test_get_dataset_settings_not_found(mocked_client):
    name = "test_get_dataset_settings"
    rb.delete(name)
    create_dataset(mocked_client, name)

    response = fetch_settings(mocked_client, name)
    assert response.status_code == 404


def test_delete_settings(mocked_client):
    name = "test_delete_settings"
    rb.delete(name)

    create_dataset(mocked_client, name)
    assert create_settings(mocked_client, name).status_code == 200

    response = mocked_client.delete(
        f"/api/datasets/{TaskType.text_classification}/{name}/settings"
    )
    assert response.status_code == 200
    assert fetch_settings(mocked_client, name).status_code == 404


def fetch_settings(mocked_client, name):
    return mocked_client.get(
        f"/api/datasets/{TaskType.text_classification}/{name}/settings"
    )
