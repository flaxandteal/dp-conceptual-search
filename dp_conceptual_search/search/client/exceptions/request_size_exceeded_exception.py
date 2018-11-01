class RequestSizeExceededException(Exception):
    def __init__(self, request_size, max_request_size):
        super(RequestSizeExceededException, self).__init__("Max request size exceeded: Got {actual} [max={max}]"
                                                           .format(actual=request_size, max=max_request_size))
