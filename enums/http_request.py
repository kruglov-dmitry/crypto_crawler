class HTTP_REQUEST(object):
    GET = 1
    POST = 2


def get_http_request_type_by_id(http_request_id):
    return {
        HTTP_REQUEST.GET: "GET",
        HTTP_REQUEST.POST: "POST"
    }[http_request_id]
