def is_error(json_document):
    """

    :param json_document:
    :return:
    """

    if json_document is None or "error" in json_document:
        return True

    return False