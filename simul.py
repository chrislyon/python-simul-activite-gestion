#!/usr/bin/env python
# -*- coding: utf-8 -*- 


import multiprocessing
import initialisation
import sqlite3
import random
import time
import os, sys

POLL_TIMEOUT = 1

BASE_FILE = "test.dbf"

class Client(multiprocessing.Process):
    def __init__(self, n, kill_q, ent):
        multiprocessing.Process.__init__(self)
        self.no = n
        self.name = "CLI%04d" % n
        self.kill_q = kill_q
        self.ent = ent

    def run(self):
        print "Client : %s " % self.no
        kill_flag = False
        while not kill_flag:
            ## ais je recu qq chose ?
            while self.ent.poll(POLL_TIMEOUT):
                msg = self.ent.recv()
                print "Client : %s : recv : %s" % ( self.no, msg )
                self.ent.send("Client : %s : OK [%s]" % (self.no, msg ))

            ## On envoi qq chose ?
            if random.choice(range(100)) > 50:
                self.ent.send('Client : %s envoi de commande' % self.no )
            else:
                sleep_time = 5
                print 'Client %s en attente' % self.no
                time.sleep(sleep_time)

            ## Si Kill Flag on arrete
            if not self.kill_q.empty():
                kill_flag = self.kill_q.get()
                print 'KILL FLAG => %s' % self.no
        return

class Entreprise(multiprocessing.Process):
    def __init__(self, kill_q, clients ):
        multiprocessing.Process.__init__(self)
        self.kill_q = kill_q
        self.clients = clients
        self.name = "ENTREPRISE"

    def run(self):
        print "ENT : Ouverture"
        for cli in self.clients:
            cli.send('Envoi du catalogue' )

        t = 1
        print "ENT :  Waiting "
        time.sleep(t)

        ## Boucle principale
        shutdown = False

        while not shutdown:
            print "ENT : loop"
            for client in self.clients:
                while client.poll(POLL_TIMEOUT):
                    print 'Recu du client : %s' % client.recv()

            ## ON ferme ?
            if not self.kill_q.empty():
                shutdown = self.kill_q.get()
                print 'ENT : SHUTDOWN ...'

        print "ENT :  Fermeture "
        return



## -------------
## Lancement 
## -------------
def compute():
    #initialisation.init_base()

    processes = []
    ## Creation clients
    clients = []
    kill_queue = multiprocessing.Queue()

    ## Initialisation 
    ## Creation des clients
    nb_client = 5
    for n in range(nb_client):
        ent_conn, cli_conn = multiprocessing.Pipe()
        clients.append(ent_conn)
        c = Client(n, kill_queue, cli_conn)
        c.start()
        processes.append(c)
    ## Creation de l'entreprise
    Ent = Entreprise( kill_queue, clients )
    processes.append(Ent)
    Ent.start()
    ## Attente
    time.sleep(5)
    ## Arret
    print "====> sending kill"
    for process in processes:
        print process.name
        kill_queue.put(True)
                    
    time.sleep(10)
    print "====> Join"
    processes.reverse()
    for process in processes:
        print process.name
        process.join(5)

## ---------------
## Main
## ---------------
if __name__ == '__main__':
    compute()
