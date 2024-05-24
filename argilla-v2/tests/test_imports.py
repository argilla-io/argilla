def test_import_v1():
    from argilla_bundle import v1
    assert v1.__version__


def test_import_v2():
    from argilla_bundle import v2
    assert v2.__version__
