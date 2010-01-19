import base64
import sys

import unittest
import mock

import pyrrhic
import pyrrhic.ui
import pyrrhic.commands
import pyrrhic.http

def build_mock_response(mock_get, code=200, msg='OK', headers={}, data=''):
    mock_response = mock.Mock()
    
    # The API for the response object changes slightly between httplib and urllib2.
    # Set attributes that have different names in each twice so the resultant object
    # can be used anywhere.
    mock_response.code = mock_response.status = code
    mock_response.msg = mock_response.reason = msg
    mock_response.info.return_value = headers.items()
    mock_response.read.return_value = data
    mock_get.return_value = mock_response
    return mock_response

class Writeable(object):
    
    def __init__(self):
        self.written = []
    
    def write(self, str):
        self.written.append(str)

class StdoutRedirectorBase(unittest.TestCase):

    def _stdout(self):
        sys.stdout = Writeable()
        sys.stderr = Writeable()
        return sys.stdout, sys.stderr
        
    def tearDown(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        

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

    @mock.patch('urllib2.OpenerDirector.open')
    def testGet(self, mock_open):
        mock_response = build_mock_response(mock_open)
        mock_open.return_value = mock_response        
        response = self.resource.get()
        self.failUnless(response is mock_response)
        
    @mock.patch('httplib.HTTPConnection.getresponse')
    @mock.patch('httplib.HTTPConnection.request')
    def test40x(self, mock_request, mock_getresponse):
        mock_response = build_mock_response(mock_getresponse, code=405, msg='Method not allowed')
        response = self.resource.get()
        self.assertEqual(405, response.code)
        
    @mock.patch('urllib2.OpenerDirector.open')
    @mock.patch('pyrrhic.http.Request.__init__')
    def testPostPutData(self, mock_ctor, mock_open):
        mock_response = build_mock_response(mock_open)
        post_data = {'post': 'data'}
        mock_ctor.return_value = None
        for m in 'put', 'post':
            getattr(self.resource, m)(data=post_data)
            args, kwargs = mock_ctor.call_args
            self.assertEqual(('http://foo.com:8080/resource',), args)
            self.assertEqual({
                'req_method': m.upper(),
                'data': 'post=data'
            }, kwargs)
        
    @mock.patch('urllib2.OpenerDirector.open')
    @mock.patch('pyrrhic.http.Request.add_header')
    def testAuthentication(self, mock_add_header, mock_open):
        mock_response = build_mock_response(mock_open)
        self.assertEqual(False, self.resource.has_authentication)
        self.resource.set_authentication('username', 'password')
        self.assertEqual(True, self.resource.has_authentication)
        self.resource.get()
        self.assertEqual(True, mock_add_header.called)
        args, kw = mock_add_header.call_args
        expected = 'Basic ' + base64.b64encode('username:password')
        self.assertEqual(('Authorization', expected),
                         args)
        self.assertEqual({}, kw)

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

    def testPut(self):
        command, args = self.p.parse('put')
        self.assertEqual(pyrrhic.commands.PutCommand, command)
        self.assertEqual(tuple(), args)

    def testPost(self):
        command, args = self.p.parse('post')
        self.assertEqual(pyrrhic.commands.PostCommand, command)
        self.assertEqual(tuple(), args)
        
    def testPostData(self):
        command, args = self.p.parse('post :username=foo')
        self.assertEqual(pyrrhic.commands.PostCommand, command)
        self.assertEqual((':username=foo',), args)

    def testDelete(self):
        command, args = self.p.parse('del')
        self.assertEqual(pyrrhic.commands.DeleteCommand, command)
        self.assertEqual(tuple(), args)

    def testDelete(self):
        command, args = self.p.parse('opts')
        self.assertEqual(pyrrhic.commands.OptionsCommand, command)
        self.assertEqual(tuple(), args)
        
    def testUnknown(self):
        command, args = self.p.parse('doesnotexist')
        self.assertEqual(pyrrhic.commands.UnknownCommand, command)
        self.assertEqual(tuple(), args)
        
    def testAuth(self):
        command, args = self.p.parse('auth username password')
        self.assertEqual(pyrrhic.commands.AuthCommand, command)
        self.assertEqual(('username', 'password'), args)

        
class QuitCommandTestCase(StdoutRedirectorBase):

    def testQuit(self):
        out, err = self._stdout()        
        c = pyrrhic.commands.QuitCommand({})
        c.run()
        self.assertEqual(['Press ^D (Ctrl-D) to quit', '\n'], out.written)
        
    def testQuitValidation(self):
        # Quit's validation always passes
        c = pyrrhic.commands.QuitCommand({})
        c.validate()
        
    def testShowEmpty(self):
        out, err = self._stdout()       
        c = pyrrhic.commands.ShowCommand({})
        c.run()
        self.assertEqual([], out.written)
        

class HelpCommandTestCase(StdoutRedirectorBase):
    
    def testHelp(self):
        out, err = self._stdout()        
        c = pyrrhic.ui.HelpCommand({})
        c.run()
        
        # Don't bet on what commands are there. Just check for the help 
        # command!
        expected = 'h: ' + c.__doc__.strip()
        found = False
        for line in out.written:
            if line == expected:
                found = True
                break
        self.failUnless(found)


class UnknownCommandTestCae(StdoutRedirectorBase):

    def testUnknown(self):
        out, err = self._stdout()        
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
        
        
class AuthCommandTestCase(StdoutRedirectorBase):
    
    def setUp(self):
        self.resources = {
            '__default__': pyrrhic.Resource('http://foo.com/')
        }
        
        self.c = pyrrhic.commands.AuthCommand(self.resources)
    
    def testAuthValidation(self):
        c = pyrrhic.commands.AuthCommand(self.resources)
        
        # If a username and password aren't provided, then we should
        # get a validation error
        self.assertRaises(pyrrhic.commands.ValidationError, self.c.validate)
        self.assertRaises(pyrrhic.commands.ValidationError, self.c.validate, 
                          'username')
        self.c.validate('username', 'password')

        # If you provide three args, the last arg is interpreted as a resource.
        self.c.validate('username', 'password', '__default__')
        
        # Referring to a non-existent resource should cause a validation error
        self.assertRaises(pyrrhic.commands.ValidationError, self.c.validate, 
                          'username', 'password', 'foo')
                          
    @mock.patch('pyrrhic.Resource.set_authentication')
    def testAuthSetsResource(self, mock_set_authentication):
        self.c.run('username', 'password')
        self.assertEqual(True, mock_set_authentication.called)
        args, kw = mock_set_authentication.call_args
        self.assertEqual(('username', 'password'), args)
        self.assertEqual({}, kw)
        
        
class ShowCommandTestCase(StdoutRedirectorBase):
    
    def testShowValidation(self):
        # Show's validation always passes
        c = pyrrhic.commands.ShowCommand({})
        c.validate()
        
    def testShowResources(self):
        out, err = self._stdout()        
        c = pyrrhic.commands.ShowCommand({
            '__default__': pyrrhic.Resource('http://foo.com')
        })
        c.run()
        self.assertEqual(['__default__\t\thttp://foo.com:80','\n'], out.written)
        
    def testShowAuth(self):
        # When there are credentials set, show the resource with a *
        out, err = self._stdout()        
        r = pyrrhic.Resource('http://foo.com')
        r.set_authentication('username', 'password')
        c = pyrrhic.commands.ShowCommand({
            '__default__': r
        })
        c.run()
        self.assertEqual(['__default__\t\t*http://foo.com:80','\n',], out.written)


class RestCommandsTestCaseBase(object):

    command_class = None

    def testCommandNoDefault(self):
        # If there's no default resource, we should get a validation error
        c = self.command_class({})
        self.assertRaises(pyrrhic.commands.ValidationError, c.validate)
        
    def testCommandBadResource(self):
        # If a named resource is supplied that doesn't exist, we should
        # also get a validation error
        c = self.command_class({})
        self.assertRaises(pyrrhic.commands.ValidationError, c.validate, 'foo')

    def testValidateDefault(self):
        # If a default is present, validation should be OK
        resources = {'__default__': pyrrhic.Resource('http://foo.com')}
        c = self.command_class(resources)
        c.validate()
        
    def testNotDefaultValidation(self):
        # If a non-default is specified and is present, that's OK too
        resources = {'foo': pyrrhic.Resource('http://foo.com')}
        c = self.command_class(resources)
        c.validate('foo')

    # Overridden in subclass
    def testDoCommandDefault(self, mock_get):
        mock_response = build_mock_response(mock_get)
        resources = {'__default__': pyrrhic.Resource('http://foo.com')}
        c = self.command_class(resources)
        c.run()
        self.assertEqual(True, mock_get.called)
        
    # Overridden in subclass
    def testPrintResults(self, mock_get):
        out, err = self._stdout()        
        mock_response = build_mock_response(mock_get, headers={'header':'value'}, data='Body Content')
        resources = {'__default__': pyrrhic.Resource('http://foo.com')}
        c = self.command_class(resources)
        c.run()
        written = [x for x in out.written if x != '\n']
        self.assertEqual('200 OK', written[0])
        self.assertEqual('header: value', written[1])
        self.assertEqual('Body Content', written[2])
        
        
class GetCommandTestCase(StdoutRedirectorBase, RestCommandsTestCaseBase):
    
    command_class = pyrrhic.commands.GetCommand
    
    @mock.patch('pyrrhic.Resource.get')
    def testDoCommandDefault(self, mock_get):
        super(GetCommandTestCase, self).testDoCommandDefault(mock_get)

    @mock.patch('pyrrhic.Resource.get')
    def testPrintResults(self, mock_get):
        super(GetCommandTestCase, self).testPrintResults(mock_get)
        
        
class PostCommandTestCase(StdoutRedirectorBase, RestCommandsTestCaseBase):
    
    command_class = pyrrhic.commands.PostCommand
        
    @mock.patch('pyrrhic.Resource.post')
    def testDoCommandDefault(self, mock_get):
        super(PostCommandTestCase, self).testDoCommandDefault(mock_get)

    @mock.patch('pyrrhic.Resource.post')
    def testPrintResults(self, mock_get):
        super(PostCommandTestCase, self).testPrintResults(mock_get)
        
    @mock.patch('pyrrhic.Resource.post')
    def testPostData(self, mock_post):
        mock_response = build_mock_response(mock_post, headers={'header':'value'}, data='Body Content')
        resources = {'__default__': pyrrhic.Resource('http://foo.com')}
        c = self.command_class(resources)
        c.run(':key=value')
        args, kwargs = mock_post.call_args
        self.assertEqual({'data': {'key': ['value']}}, kwargs)
        self.assertEqual(tuple(), args)
        
class PutCommandTestCase(StdoutRedirectorBase, RestCommandsTestCaseBase):
    
    command_class = pyrrhic.commands.PutCommand
        
    @mock.patch('pyrrhic.Resource.put')
    def testDoCommandDefault(self, mock_get):
        super(PutCommandTestCase, self).testDoCommandDefault(mock_get)

    @mock.patch('pyrrhic.Resource.put')
    def testPrintResults(self, mock_get):
        super(PutCommandTestCase, self).testPrintResults(mock_get)        

    @mock.patch('pyrrhic.Resource.put')
    def testPutData(self, mock_put):
        mock_response = build_mock_response(mock_put, headers={'header':'value'}, data='Body Content')
        resources = {'__default__': pyrrhic.Resource('http://foo.com')}
        c = self.command_class(resources)
        c.run(':key=value')
        args, kwargs = mock_put.call_args
        self.assertEqual({'data': {'key': ['value']}}, kwargs)
        self.assertEqual(tuple(), args)
        
        
class DeleteCommandTestCase(StdoutRedirectorBase, RestCommandsTestCaseBase):
    
    command_class = pyrrhic.commands.DeleteCommand
        
    @mock.patch('pyrrhic.Resource.delete')
    def testDoCommandDefault(self, mock_get):
        super(DeleteCommandTestCase, self).testDoCommandDefault(mock_get)

    @mock.patch('pyrrhic.Resource.delete')
    def testPrintResults(self, mock_get):
        super(DeleteCommandTestCase, self).testPrintResults(mock_get)        


class OptionsCommandTestCase(StdoutRedirectorBase, RestCommandsTestCaseBase):
    
    command_class = pyrrhic.commands.OptionsCommand
        
    @mock.patch('pyrrhic.Resource.options')
    def testDoCommandDefault(self, mock_get):
        super(OptionsCommandTestCase, self).testDoCommandDefault(mock_get)

    @mock.patch('pyrrhic.Resource.options')
    def testPrintResults(self, mock_get):
        super(OptionsCommandTestCase, self).testPrintResults(mock_get)        
        
    
class CustomRequestTestCase(unittest.TestCase):
    
    def testFallbackGet(self):
        request = pyrrhic.http.Request('http://foo.com/')
        self.assertEqual('GET', request.get_method())
        
    def testFallbackPost(self):
        request = pyrrhic.http.Request('http://foo.com/', data='foo')
        self.assertEqual('POST', request.get_method())
        
    def testOverride(self):
        request = pyrrhic.http.Request('http://foo.com/', req_method='OPTIONS')
        self.assertEqual('OPTIONS', request.get_method())
        request = pyrrhic.http.Request('http://foo.com/', req_method='PUT')
        self.assertEqual('PUT', request.get_method())
        request = pyrrhic.http.Request('http://foo.com/', req_method='DELETE')
        self.assertEqual('DELETE', request.get_method())
        

class UiTestCase(StdoutRedirectorBase):
        
    def setUp(self):
        resources = {'__default__': pyrrhic.Resource('http://foo.com')}
        self.command = pyrrhic.commands.GetCommand(resources)
        self.out, self.err = self._stdout()
        
    @mock.patch('pyrrhic.commands.GetCommand.run')
    def testUrlError(self, mock_run):
        import urllib2
        mock_run.side_effect = urllib2.URLError('dummy')
        pyrrhic.ui.run_command(self.command, tuple())        
        written = ''.join(self.err.written)
        self.failUnless(written.find('URLError') > -1)
        
    @mock.patch('pyrrhic.commands.GetCommand.run')
    def testGaiErrro(self, mock_run):
        import socket
        mock_run.side_effect = socket.gaierror('dummy')
        pyrrhic.ui.run_command(self.command, tuple())        
        written = ''.join(self.err.written)
        self.failUnless(written.find('gaierror') > -1)

    