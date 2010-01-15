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

class StdoutRedirectorBase(unittest.TestCase):

    def _stdout(self):
        sys.stdout = Writeable()
        return sys.stdout
        
    def tearDown(self):
        sys.stdout = sys.__stdout__
        

class ResourceTestCase(StdoutRedirectorBase):
    
    def setUp(self):
        self.resource = pyrrhic.Resource('http://foo.com:8080/resource')
        
    def testScheme(self):
        # Note that the URL scheme defaults to http if none is
        # provided
        r = pyrrhic.Resource('foo.com')
        self.assertEqual('http://foo.com:80', r.url)
        
    def testPort(self):
        # Port defaults to 80 for http, and 443 for https
        r = pyrrhic.Resource('http://foo.com')
        self.assertEqual('http://foo.com:80', r.url)
        r = pyrrhic.Resource('https://foo.com')
        self.assertEqual('https://foo.com:443', r.url)
        r = pyrrhic.Resource('foo.com:123')        
        self.assertEqual('http://foo.com:123', r.url)
        
    def testGet(self):
        mock_request = mock.Mock()
        response = mock.Mock()
        mock_getresponse = mock.Mock(return_value=response)
        response.status = 200
        response.read.return_value = 'This is the response body'
        response.getheaders.return_value = []
        
        import httplib
        real_ctor = httplib.HTTPConnection.__init__
        args = []
        kwargs = {}
        def fake_ctor(*ctor_args, **ctor_kwargs):
            for arg in ctor_args:
                args.append(arg)
                kwargs.update(ctor_kwargs)
            return real_ctor(*ctor_args, **ctor_kwargs)
        
        with testfixtures.Replacer() as r:
            r.replace('httplib.HTTPConnection.request', mock_request)
            r.replace('httplib.HTTPConnection.getresponse', mock_getresponse)
            r.replace('httplib.HTTPConnection.__init__', fake_ctor)
            status, reason, headers, body = self.resource.get()

        self.assertEqual({}, kwargs)
        self.assertEqual('foo.com:8080', args[1])
    
        self.assertEqual(200, status)
        self.assertEqual('This is the response body', body)    
        self.assertEqual('http://foo.com:8080/resource', self.resource.url)
        
        
class CommandParserTestCase(StdoutRedirectorBase):
    
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
        
    def testShow(self):
        command, args = self.p.parse('s')
        self.assertEqual(pyrrhic.commands.ShowCommand, command)
        self.assertEqual(tuple(), args)
        
    def testGet(self):
        command, args = self.p.parse('get')
        self.assertEqual(pyrrhic.commands.GetCommand, command)
        self.assertEqual(tuple(), args)
        
    def testUnknown(self):
        command, args = self.p.parse('doesnotexist')
        self.assertEqual(pyrrhic.commands.UnknownCommand, command)
        self.assertEqual(tuple(), args)
        
        
class QuitCommandTestCase(StdoutRedirectorBase):

    def testQuit(self):
        out = self._stdout()
        c = pyrrhic.commands.QuitCommand({})
        c.run()
        self.assertEqual(['Press ^D (Ctrl-D) to quit', '\n'], out.written)
        
    def testQuitValidation(self):
        # Quit's validation always passes
        c = pyrrhic.commands.QuitCommand({})
        c.validate()
        
    def testShowEmpty(self):
        out = self._stdout()
        c = pyrrhic.commands.ShowCommand({})
        c.run()
        self.assertEqual([], out.written)
        

class UnknownCommandTestCae(StdoutRedirectorBase):

    def testUnknown(self):
        out = self._stdout()
        c = pyrrhic.commands.UnknownCommand({})
        c.run()
        self.assertEqual(['Unknown command', '\n'], out.written)

    def testUnknownValidation(self):
        # Unknown validation is a no-op
        c = pyrrhic.commands.UnknownCommand({})
        c.validate()
        
class ResourceCommandTestCase(StdoutRedirectorBase):
        
    def testResourceValidation(self):
        resources = {}
        c = pyrrhic.commands.ResourceCommand(resources)
        self.assertRaises(pyrrhic.commands.ValidationError, c.validate)

        # If a URL is present but doesn't start with http or https, then
        # it should also fail to validate
        self.assertRaises(pyrrhic.commands.ValidationError, c.validate, 'ftp://foo.bar')

        c.validate('http://foo.com')
        c.validate('https://foo.com')

        # A straight hostname is also OK, http will be assumed
        c.validate('foo.com')

    def testResource(self):
        resources = {}
        c = pyrrhic.commands.ResourceCommand(resources)
        c.run('http://foo.com')
        self.assertEqual(1, len(resources.items()))
        self.failUnless(resources.has_key('__default__'))

        unnamed = resources['__default__']
        self.failUnless(isinstance(unnamed, pyrrhic.Resource))

        c.run('http://bar.com')
        unnamed2 = resources['__default__']
        self.failIf(unnamed is unnamed2)

        c.run('http://cheese.com', 'cheese')
        self.failUnless(resources.has_key('cheese'))
        cheese = resources['cheese']
        self.failIf(cheese is unnamed2)
        
        
class ShowCommandTestCase(StdoutRedirectorBase):
    
    def testShowValidation(self):
        # Show's validation always passes
        c = pyrrhic.commands.ShowCommand({})
        c.validate()
        
    def testShowResources(self):
        out = self._stdout()
        c = pyrrhic.commands.ShowCommand({
            '__default__': pyrrhic.Resource('http://foo.com')
        })
        c.run()
        self.assertEqual(['__default__\t\thttp://foo.com:80','\n'], out.written)

        
class GetCommandTestCase(StdoutRedirectorBase):
    
    def testGetCommandNoDefault(self):
        # If there's no default resource, we should get a validation error
        c = pyrrhic.commands.GetCommand({})
        self.assertRaises(pyrrhic.commands.ValidationError, c.validate)
        
    def testGetCommandBadResource(self):
        # If a named resource is supplied that doesn't exist, we should
        # also get a validation error
        c = pyrrhic.commands.GetCommand({})
        self.assertRaises(pyrrhic.commands.ValidationError, c.validate, 'foo')

    def testValidateDefault(self):
        # If a default is present, validation should be OK
        resources = {'__default__': pyrrhic.Resource('http://foo.com')}
        c = pyrrhic.commands.GetCommand(resources)
        c.validate()
        
    def testNotDefaultValidation(self):
        # If a non-default is specified and is present, that's OK too
        resources = {'foo': pyrrhic.Resource('http://foo.com')}
        c = pyrrhic.commands.GetCommand(resources)
        c.validate('foo')
        
    @mock.patch('pyrrhic.Resource.get')
    def testGetCommandDefault(self, mock_get):
        resources = {'__default__': pyrrhic.Resource('http://foo.com')}
        c = pyrrhic.commands.GetCommand(resources)
        c.run()
        self.assertEqual(True, mock_get.called)