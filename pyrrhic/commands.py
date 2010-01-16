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
        if len(args) == 0 and not self.resources.has_key('__default__'):
            raise ValidationError, 'No default resource and no resource specified'
        elif len(args) == 1 and not self.resources.has_key(args[0]):
            raise ValidationError, 'Specified resource not found'

    def run(self, *args):
        if len(args) == 0:
            name = '__default__'
        else:
            name = args[0]
        method = getattr(self.resources[name], self.method)
        status, reason, headers, data = method()
        if status or reason:
            print '%s %s' % (status, reason)
        for header, value in headers.items():
            print "%s: %s" % (header, value)
        print data


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


        
            