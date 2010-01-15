from pyrrhic.commands import RESOURCE

class CommandParser(object):

    commands = {
        'r': RESOURCE
    }
    
    def parse(self, str):
        bits = str.split()
        cmd = bits[0].lower()
        return self.commands[cmd], tuple(bits[1:])
    

def console():
    pass
