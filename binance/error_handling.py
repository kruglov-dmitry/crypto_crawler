def is_error(json_document):
    """
    Based on https://github.com/binance-exchange/binance-official-api-docs/blob/master/errors.md

    # HTTP Responce code 200, {u'msg': u"Timestamp for this request was 1000ms ahead of the server's time.", u'code': -1021}

    :param json_document: 
    :return: 
    """
    
    if json_document is None:
        return True

    if "code" in json_document and "msg" in json_document:
        return True

    return False
