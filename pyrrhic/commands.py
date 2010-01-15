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
    This command just prints a message out.
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