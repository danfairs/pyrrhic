import pyrrhic.commands

class CommandParser(object):

    commands = {
        'r': pyrrhic.commands.ResourceCommand,
        'q': pyrrhic.commands.QuitCommand,
        's': pyrrhic.commands.ShowCommand,
    }
    
    def parse(self, str):
        bits = str.split()
        cmd = bits[0].lower()
        return self.commands[cmd], tuple(bits[1:])
    
    
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
                try:
                    c.validate(args)
                except pyrrhic.commands.ValidationError, e:
                    print "Error: %s" % str(e)
                    continue
                c.run(args)
        except EOFError:
            print
            exit = True
    