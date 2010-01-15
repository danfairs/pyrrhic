import httplib
import testfixtures
import urllib
import urlparse

HTTP_VERBS = (u'GET', u'POST', u'PUT', u'DELETE')

class Resource(object):
    
    headers = {
        'Content-type': 'application/xml'
    }
    
    def __init__(self, url):
        """
        Create a Resource instance, bound to a URL. The URL must start with http: or https:
        >>> r = Resource(u'ftp://something')
        ValueError
        """
        self.url = url
        self.parsed_url = urlparse.urlparse(url)

    def _getresponse(self, verb, params={}, headers={}):
        assert verb in HTTP_VERBS        
        if not headers:
            headers = self.headers
        conn = httplib.HTTPConnection('%s://%s' % self.parsed_url[:2])
        url = urlparse.urlunparse(('', '') + self.parsed_url[2:])
        params = urllib.urlencode(params, headers)
        conn.request(verb, self.parsed_url.path, params, headers)
        response = conn.getresponse()
        data = response.read()
        return response.status, response.reason, dict(response.getheaders()), data

    def get(self):
         return self._getresponse('GET')

    def put(self):
        return self._getresponse('PUT')
        
    def post(self):
        return self._getresponse('POST')
        
    def delete(self):
        return self._getresponse('DELETE')