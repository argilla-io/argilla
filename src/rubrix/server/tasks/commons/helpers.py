def takeuntil(iterable, limit: int):
    """
    Iterate over inner iterable until a count limit

    Parameters
    ----------
    iterable:
        The inner iterable
    limit:
        The limit

    Returns
    -------

    """
    count = 0
    for e in iterable:
        if count < limit:
            yield e
            count += 1
        else:
            break
