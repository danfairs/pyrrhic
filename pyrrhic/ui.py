import readline
import pyrrhic.commands
import urllib
import urllib2
import socket

# HelpCommand is in the ui module because it's nothing to do with core
# functionality
class HelpCommand(pyrrhic.commands.BaseCommand):
    """
    Prints out some help on all commands.
    """

    def run(self, *args):
        for opt, cls in REGISTERED_COMMANDS.items():
            doc = ' '.join(cls.__doc__.split())
            print "%s: %s" % (opt, doc)

REGISTERED_COMMANDS = {
    'h': HelpCommand,
    'r': pyrrhic.commands.ResourceCommand,
    'q': pyrrhic.commands.QuitCommand,
    's': pyrrhic.commands.ShowCommand,
    'get': pyrrhic.commands.GetCommand,
    'put': pyrrhic.commands.PutCommand,
    'post': pyrrhic.commands.PostCommand,
    'del': pyrrhic.commands.DeleteCommand,
    'opts': pyrrhic.commands.OptionsCommand,
    'auth': pyrrhic.commands.AuthCommand,
}


class CommandParser(object):

    def parse(self, str):
        bits = str.split()
        cmd = bits[0].lower()
        command = REGISTERED_COMMANDS.get(cmd, pyrrhic.commands.UnknownCommand)
        return command, tuple(bits[1:])
        

def run_command(command, args):
    """ Validate and run the supplied command """
    try:
        command.validate(*args)
    except pyrrhic.commands.ValidationError, e:
        print "Error: %s" % str(e)
        return
    try:
        command.run(*args)
    except (urllib2.URLError, socket.gaierror), e:
        import traceback
        traceback.print_exc()
    
    
def console():
    p = CommandParser()
    resources = {}
    exit = False
    while not exit:
        try:
            inp = raw_input('pyr >>> ')
            if inp:
                command, args = p.parse(inp)
                c = command(resources)
                run_command(c, args)
        except EOFError:
            print
            exit = True
    