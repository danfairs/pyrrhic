import urllib2

_marker = object()

class Request(urllib2.Request):
    """ Subclass of urllib2.Request that can do PUT, DELETE and OPTIONS """
    
    def __init__(self, url, data=None, headers={},
                 origin_req_host=None, unverifiable=False,
                 req_method=_marker):
        urllib2.Request.__init__(self, url, data, headers, origin_req_host,
                 unverifiable)
        self.req_method = req_method
        
    def get_method(self):
        if self.req_method is _marker:
            # If a method wasn't set, fall back to the default approach
            return urllib2.Request.get_method(self)
        return self.req_method
        

class PyrrhicHTTPErrorHandler(urllib2.HTTPDefaultErrorHandler):
    
    def http_error_default(self, req, fp, code, msg, hdrs):
        return fp