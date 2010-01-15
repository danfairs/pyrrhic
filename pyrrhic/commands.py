import pyrrhic

class BaseCommand(object):
    
    def __init__(self, resources):
        self.resources = resources

class ResourceCommand(BaseCommand):
    """
    This command adds a new resource.
    """
    
    def run(self, *args):
        url = args[0]
        try:
            name = args[1]
        except IndexError:
            name = '__unnamed__'
        self.resources[name] = pyrrhic.Resource(url)
        

class QuitCommand(BaseCommand):
    """
    This command just prints a message out.
    """
    def run(self, *args):
        print 'Press ^D (Ctrl-D) to quit'
