import cmd

class Simulator(cmd.Cmd):
    """Simple command processor example."""
    
    def do_greet(self, person):
        if person:
            print "hi,", person
        else:
            print 'hi'
    
    def help_greet(self):
        print '\n'.join([ 'greet [person]',
                           'Greet the named person',
                           ])
    
    def do_EOF(self, line):
        return True

if __name__ == '__main__':
    Simulator().cmdloop()
