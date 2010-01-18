import urlparse
import pyrrhic

class ValidationError(Exception):
    """ There was a problem validating the arguments """


class BaseCommand(object):
    
    def __init__(self, resources):
        self.resources = resources

    def validate(self, *args):
        """
        Validate that the args are OK. Throws a `ValidationError` if not.
        """
        pass


class UnknownCommand(BaseCommand):
    """ This command prints a message that an unknown command was invoked """
    def run(self, *args):
        print 'Unknown command'

class ResourceCommand(BaseCommand):
    """
    This command adds a new resource.
    """
    
    def validate(self, *args):
        if len(args) == 0:
            raise ValidationError, 'Please specify a URL'
        url = args[0]
        scheme_end = url.find('://')
        if scheme_end > -1:
            scheme = url[:scheme_end]
            if scheme not in ('http', 'https'):
                raise ValidationError, 'URL must start with http:// or https://'
        
    def run(self, *args):
        url = args[0]
        try:
            name = args[1]
        except IndexError:
            name = '__default__'
        self.resources[name] = pyrrhic.Resource(url)

        
class QuitCommand(BaseCommand):
    """
    Print help on how to quit. (Hint: Ctrl-D)
    """
    def run(self, *args):
        print 'Press ^D (Ctrl-D) to quit'


class ShowCommand(BaseCommand):
    """ 
    This command prints out all named resources
    """
    def run(self, *args):
        for name, resource in self.resources.items():
            print "%s\t\t%s" % (name, resource.url)


class RestCommand(BaseCommand):            
    """ Base class for the REST commands, which all have similar 
        semantics
    """
    
    method = None
    
    def validate(self, *args):
        name, kwargs = self._parse_resource_data(*args)
        if not self.resources.has_key(name):
            raise ValidationError, 'Specified resource not found'

    def run(self, *args):
        name, data = self._parse_resource_data(*args)
        kw = {}
        if data:
            kw['data'] = data
        response = getattr(self.resources[name], self.method)(**kw)
        status = response.code
        reason = response.msg
        headers = dict(response.info())
        data = response.read()
        if status or reason:
            print '%s %s' % (status, reason)
        for header, value in headers.items():
            print "%s: %s" % (header, value)
        print data

    def _parse_resource_data(self, *args):
        # Parse out a resource name and/or data. If the first
        # element starts with a colon, then it's data. Otherwise,
        # it'll be the name of the resource, and the rest will be data.
        name = '__default__'
        args = list(args)
        kw = {}
        if args:
            if not args[0].startswith(':'):
                name = args.pop(0)
            if args:
                kw = urlparse.parse_qs(args[0][1:])
        return name, kw
        

class GetCommand(RestCommand):
    """
    This command causes the named (or default) resource to do a GET
    """
    method = 'get'
                             
                    
class PostCommand(RestCommand):
    """
    This command causes the named (or default) resource to do a POST
    """
    method = 'post'


class DeleteCommand(RestCommand):
    """
    This command causes the named (or default) resource to do a DELETE
    """
    method = 'delete'


class PutCommand(RestCommand):
    """
    This command causes the named (or default) resource to do a PUT
    """
    method = 'put'
    

class OptionsCommand(RestCommand):
    """
    This command causes the named (or default) resource to do an OPTIONS
    """
    method = 'options'


        
            