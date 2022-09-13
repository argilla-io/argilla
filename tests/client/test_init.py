from rubrix.client import api


def test_resource_leaking_with_several_init(mocked_client):
    dataset = "test_resource_leaking_with_several_init"
    api.delete(dataset)

    # TODO: review performance in Windows. See https://github.com/recognai/rubrix/pull/1702
    for i in range(0, 20):
        api.init()

    for i in range(0, 10):
        api.init()
        api.log(
            api.TextClassificationRecord(text="The text"), name=dataset, verbose=False
        )

    assert len(api.load(dataset)) == 10


def test_init_with_extra_headers(mocked_client):
    expected_headers = {
        "X-Custom-Header": "Mocking rules!",
        "Other-header": "Header value",
    }
    api.init(extra_headers=expected_headers)
    active_api = api.active_api()

    for key, value in expected_headers.items():
        assert (
            active_api.client.headers[key] == value
        ), f"{key}:{value} not in client headers"
