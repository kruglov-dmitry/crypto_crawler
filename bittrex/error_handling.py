def is_error(json_document):
    """

    :param json_document:
    :return:
    """

    if json_document is None or "result" not in json_document:
        return True

    if (json_document["result"] is None and "success" not in json_document) or \
            ("success" in json_document and json_document["success"] is False):
        return True

    return False
