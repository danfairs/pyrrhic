from __future__ import with_statement

import unittest
import mock
import testfixtures

import pyrrhic
import pyrrhic.ui
import pyrrhic.commands

class ResourceTestCase(unittest.TestCase):
    
    def setUp(self):
        self.resource = pyrrhic.Resource('http://foo.com:8080/resource')

    def testGet(self):
        mock_request = mock.Mock()
        response = mock.Mock()
        mock_getresponse = mock.Mock(return_value=response)
        response.status = 200
        response.read.return_value = 'This is the response body'
        response.getheaders.return_value = []
        
        with testfixtures.Replacer() as r:
            r.replace('httplib.HTTPConnection.request', mock_request)
            r.replace('httplib.HTTPConnection.getresponse', mock_getresponse)
            status, reason, headers, body = self.resource.get()

        self.assertEqual(200, status)
        self.assertEqual('This is the response body', body)
        
        
class CommandParserTestCase(unittest.TestCase):
    
    def testResource(self):
        p = pyrrhic.ui.CommandParser()
        command, args = p.parse('r http://foo.com')
        self.assertEqual(pyrrhic.commands.RESOURCE, command)
        self.assertEqual(('http://foo.com',), args)
        