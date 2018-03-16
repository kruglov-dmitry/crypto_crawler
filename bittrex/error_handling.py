def is_error(json_document):
    """

    :param json_document:
    :return:
    """

    if json_document is None or "result" not in json_document or json_document["result"] is None:
        return True

    return False
