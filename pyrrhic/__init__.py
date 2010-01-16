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
        Create a Resource instance, bound to a URL.
        """
        parsed_url = urlparse.urlparse(url)
        if parsed_url.scheme and not parsed_url.netloc:
            # If we have a scheme but no netloc, someone's entered
            # a URL like 'foo.com:123'. Add an http://to the
            # start, and reparse.
            url = 'http://' + url
            parsed_url = urlparse.urlparse(url)
            
        if not parsed_url.scheme:
            # If no scheme was provided, then the url parsing
            # won't have worked. Reparse.
            scheme = 'http'
            url = '%s://%s' % (scheme, url)
            parsed_url = urlparse.urlparse(url)
        else:
            scheme = parsed_url.scheme

        if parsed_url.netloc.find(':') < 0:
            if scheme == 'http':
                netloc = parsed_url.netloc + ':80'
            else:
                netloc = parsed_url.netloc + ':443'
        else:
            # Already had an explicit port
            netloc = parsed_url.netloc
        
        # Normalise
        self.url = urlparse.urlunparse((scheme, netloc, parsed_url.path,
                    parsed_url.params, parsed_url.query, parsed_url.fragment))
        self.parsed_url = urlparse.urlparse(self.url)

    def _getresponse(self, verb, params={}, headers={}):
        assert verb in HTTP_VERBS        
        if not headers:
            headers = self.headers
        conn = httplib.HTTPConnection(self.parsed_url.netloc)
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
        
    def options(self):
        return self._getresponse('OPTIONS')