from __future__ import with_statement

import sys

import unittest
import mock
import testfixtures

import pyrrhic
import pyrrhic.ui
import pyrrhic.commands

class Writeable(object):
    
    def __init__(self):
        self.written = []
    
    def write(self, str):
        self.written.append(str)


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
        
        self.assertEqual('http://foo.com:8080/resource', self.resource.url)
        
class CommandParserTestCase(unittest.TestCase):
    
    def setUp(self):
        self.p = pyrrhic.ui.CommandParser()
    
    def testResource(self):
        command, args = self.p.parse('r http://foo.com')
        self.assertEqual(pyrrhic.commands.ResourceCommand, command)
        self.assertEqual(('http://foo.com',), args)
        
    def testQuit(self):
        command, args = self.p.parse('q')
        self.assertEqual(pyrrhic.commands.QuitCommand, command)
        self.assertEqual(tuple(), args)
        
        
class CommandTestCase(unittest.TestCase):

    def testQuit(self):
        out = Writeable()
        sys.stdout = out
        c = pyrrhic.commands.QuitCommand({})
        c.run()
        sys.stdout = sys.__stdout__
        self.assertEqual(['Press ^D (Ctrl-D) to quit', '\n'], out.written)
        
    def testResource(self):
        resources = {}
        c = pyrrhic.commands.ResourceCommand(resources)
        c.run('http://foo.com')
        self.assertEqual(1, len(resources.items()))
        self.failUnless(resources.has_key('__unnamed__'))
        
        unnamed = resources['__unnamed__']
        self.failUnless(isinstance(unnamed, pyrrhic.Resource))
        
        c.run('http://bar.com')
        unnamed2 = resources['__unnamed__']
        self.failIf(unnamed is unnamed2)

        c.run('http://cheese.com', 'cheese')
        self.failUnless(resources.has_key('cheese'))
        cheese = resources['cheese']
        self.failIf(cheese is unnamed2)
        

