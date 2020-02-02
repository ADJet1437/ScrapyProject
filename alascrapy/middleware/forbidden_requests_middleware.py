class ForbiddenRequestsMiddleware(object):

    # overwrite process request
    def process_response(self, request, response, spider):
        if response.status in [403, 404, 503]:
            request = spider._retry(request)
            if request:
                return request
        return response