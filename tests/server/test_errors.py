from rubrix.server.errors import GenericRubrixServerError


def test_generic_error():

    err = GenericRubrixServerError(error=ValueError("this is an error"))
    assert (
        str(err)
        == "rubrix.api.errors::GenericRubrixServerError(type=builtins.ValueError,message=this is an error)"
    )
