from rubrix.client import api


def test_resource_leaking_with_several_inits(mocked_client):
    dataset = "test_resource_leaking_with_several_inits"
    api.delete(dataset)

    for i in range(0, 20):
        api.init()

    for i in range(0, 10):
        api.init()
        api.log(
            api.TextClassificationRecord(text="The text"), name=dataset, verbose=False
        )

    assert len(api.load(dataset)) == 10
