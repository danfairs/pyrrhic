class BaseCommand(object):
    
    def __init__(self, resources):
        self.resources = resources

class Resource(BaseCommand):
    
    def run(self, *args):
        pass

class Quit(BaseCommand):
    
    def run(self, *args):
        print 'Press ^D (Ctrl-D) to quit'
