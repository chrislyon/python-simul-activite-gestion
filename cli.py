import cmd2

import multiprocessing
import time

## On affinera apres
import simul

class Instance():
    def __init__(self, name):
        self.name  = name
        self.processes = []
        self.kill_queue = multiprocessing.Queue()

        self.clients = []
        self.ent = None

        self.status = "STOPPED"

    def log(self, msg):
        print "Instance %s : %s " % (self.name, msg)

    def cr_ent(self):
        self.log("Creating Entreprise ...")
        self.ent = simul.Entreprise(self.kill_queue)
        self.processes.append( self.ent )

    def cr_clients(self, nb):
        for n in range(nb):
            self.log("Creating client : %s " % n)
            e_conn, c_conn = multiprocessing.Pipe()
            self.ent.add_client(e_conn)
            c = simul.Client(n, self.kill_queue, c_conn)
            self.clients.append(c)
            self.processes.append(c)

    def start_all(self):
        self.log("Starting clients")
        for c in self.clients:
            c.start()
        self.log("Starting Entreprise")
        self.ent.start()
        self.status = "RUNNING"

    def send_kill_all(self):
        self.log("Starting clients")
        for p in self.processes:
            self.log("Sending kill : %s " % p.name )
            self.kill_queue.put(True)
        self.status = "KILLED"

    def join_all(self):
        self.log("Joining processes")
        self.processes.reverse()
        for p in self.processes:
            self.log("join : %s " % p.name )
            p.join(5)
        self.status = "STOPPED"

    def shutdown(self):
        self.log("Shutdown started ...")
        self.send_kill_all()
        time.sleep(5)
        self.join_all()
        self.status = "STOPPED"

    def start(self):
        self.status = "STARTING"
        self.cr_ent()
        self.cr_clients(5)
        self.start_all()

class Simulator(cmd2.Cmd):
    """Simple command processor example."""
    
    INSTANCE = Instance("Entreprise")

    def do_status(self, line):
        print "Status : %s " % Simulator.INSTANCE.status

    def help_status(self):
        print '\n'.join([ 'status', 
                          "Affiche le status courant de l'instance", 
                        ])

    def do_startup(self, opt):
        Simulator.INSTANCE.start()

    def help_startup(self):
        print '\n'.join([ 'startup [name]', 
                          "Demarrage de l' instance ", 
                        ])

    def do_shutdown(self, opt):
        print "=========================  Shutdown "
        Simulator.INSTANCE.shutdown()

    def help_shutdown(self):
        print '\n'.join([ 'shutdown [temps]', 
                          "Temps en seconde", 
                        ])
    ## Example
    def do_greet(self, person):
        if person:
            print "hi,", person
        else:
            print 'hi'
    
    def help_greet(self):
        print '\n'.join([ 'greet [person]', 'Greet the named person', ])
    ## Fin de l'exemple
    
    def do_EOF(self, line):
        return True

if __name__ == '__main__':
    Simulator().cmdloop()
