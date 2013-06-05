#!/usr/bin/env python
# -*- coding: utf-8 -*- 

##
## Simulation d'activite
##

import multiprocessing
import sqlite3
import random
import time
import os, sys

import BDD

POLL_TIMEOUT = 1

BASE_FILE = "test.dbf"

class Client(multiprocessing.Process):
    def __init__(self, n, kill_q, ent):
        multiprocessing.Process.__init__(self)
        self.no = n
        self.name = "CLI%04d" % n
        self.kill_q = kill_q
        self.ent = ent

    def log(self, msg):
        print "CLIENT : %s : %s " % ( self.name, msg)

    def run(self):
        self.log(" debut ")
        kill_flag = False
        while not kill_flag:
            ## ais je recu qq chose ?
            while self.ent.poll(POLL_TIMEOUT):
                msg = self.ent.recv()
                self.log( "recv : %s" % msg )
                self.ent.send("CLI[%s] : OK [%s]" % (self.no, msg ))

            ## On envoi qq chose ?
            if random.choice(range(100)) > 50:
                self.ent.send('Client : %s envoi de commande' % self.no )
            else:
                sleep_time = 5
                self.log( 'En attente')
                time.sleep(sleep_time)

            ## Si Kill Flag on arrete
            if not self.kill_q.empty():
                kill_flag = self.kill_q.get()
                self.log( 'Recu KILL FLAG ')
        return

class Entreprise(multiprocessing.Process):
    def __init__(self, kill_q, clients ):
        multiprocessing.Process.__init__(self)
        self.kill_q = kill_q
        self.clients = clients
        self.name = "ENTREPRISE"

    def log(self, msg):
        print "ENT : %s " % msg

    def run(self):
        self.log("OUVERTURE")
        self.log("ENVOI DU CATALOGUE")
        for cli in self.clients:
            cli.send('Envoi du catalogue' )

        t = 1
        self.log("WAITING")
        time.sleep(t)

        ## Boucle principale
        shutdown = False

        while not shutdown:
            self.log("Loop")
            for client in self.clients:
                while client.poll(POLL_TIMEOUT):
                    self.log( 'Recu du client : %s' % client.recv() )

            ## ON ferme ?
            if not self.kill_q.empty():
                shutdown = self.kill_q.get()
                self.log( 'SHUTDOWN received ...' )

        self.log( "Fermeture " )
        return

## -------------
## Lancement 
## -------------
def compute():
    ## A revoir
    #BDD.init_base()

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
        print "kill : %s " % process.name
        kill_queue.put(True)
                    
    time.sleep(10)
    print "====> Joining processes"
    processes.reverse()
    for process in processes:
        print "join : %s " % process.name
        process.join(5)

## ---------------
## Main
## ---------------
if __name__ == '__main__':
    compute()
