#!/usr/bin/env python
# -*- coding: utf-8 -*- 

## ------------------------
## Simulation d'activite
## ------------------------

import multiprocessing
import sqlite3
import random
import time
import os, sys

import BDD

POLL_TIMEOUT = 1

BASE_FILE = "test.dbf"

class Message():
    def __init__(self):
        self.origine = ""
        self.text = ""
        self.cmd = ""
        self.value = None

class Client(multiprocessing.Process):
    def __init__(self, n, kill_q, ent=None):
        multiprocessing.Process.__init__(self)
        self.no = n
        self.name = "CLI%04d" % n
        self.kill_q = kill_q
        self.ent = ent
        self.en_compte = False
        self.data = {}

    def log(self, msg):
        print "CLIENT : %s : %s " % ( self.name, msg)

    def run(self):
        self.log(" debut ")
        kill_flag = False
        while not kill_flag:
            ## Si je suis connecte
            if self.ent:
                ## Suis-je identifie ?
                self.log("Identification")
                if not self.en_compte:
                    M = Message()
                    M.cmd = "IDENTIFICATION"
                    M.origine = self.name
                    self.ent.send(M)

                ## ais je recu qq chose ?
                while self.ent.poll(POLL_TIMEOUT):
                    msg = self.ent.recv()
                    self.log( "recv : %s" % msg.text )
                    #self.ent.send("CLI[%s] : OK [%s]" % (self.no, msg ))
                    if msg.cmd == "CATALOGUE":
                        self.en_compte = True
                        self.log("RECU CATALOG : %s " % msg.value )
                        self.data["CATALOGUE"] = msg.value

                ## On envoi qq chose ?
                if self.en_compte and random.choice(range(100)) > 50:
                    M = Message()
                    M.text = "ENVOI DE COMMANDE"
                    M.origine = self.name
                    M.cmd = "COMCLI"
                    M.value = self.set_COMMANDE()
                    self.ent.send(M)
                else:
                    sleep_time = 1
                    self.log( 'En attente')
                    time.sleep(sleep_time)

            ## Si Kill Flag on arrete
            if not self.kill_q.empty():
                kill_flag = self.kill_q.get()
                self.log( 'Recu KILL FLAG ')
            ## Attente
            time.sleep(1)
        return

    def set_COMMANDE(self):
        cde = []
        CAT = self.data['CATALOGUE']
        self.log("GENERATION COMMANDE")
        for produit in CAT:
            qte = random.randrange(1,100)
            cde.append( (produit, qte) )
            self.log("Pro:%s qte=%s" % (produit, qte) )
        return cde


class Entreprise(multiprocessing.Process):
    def __init__(self, kill_q ):
        multiprocessing.Process.__init__(self)
        self.kill_q = kill_q
        self.clients = []
        self.name = "ENTREPRISE"

    def log(self, msg):
        print "ENT : %s " % msg

    def add_client(self, cli):
        self.log(" Ajout de %s " % cli )
        self.clients.append(cli)

    def run(self):
        self.log("OUVERTURE")

        ## En attente on verra plus tard
        #self.log("ENVOI DU CATALOGUE")
        #for cli in self.clients:
        #    cli.send('Envoi du catalogue' )

        t = 1
        self.log("WAITING")
        time.sleep(t)

        ## Boucle principale
        shutdown = False

        while not shutdown:
            if self.clients:
                for client in self.clients:
                    while client.poll(POLL_TIMEOUT):
                        msg = client.recv()
                        self.log( 'Recu du client : %s [cmd=%s : t=%s]' % ( msg.origine, msg.cmd, msg.text ))
                        if msg.cmd == "COMCLI":
                            self.log("Recu commande : %s / %s / %s " % (msg.origine, msg.cmd, msg.value))
                        if msg.cmd == "IDENTIFICATION":
                            M = Message()
                            M.origine = self.name
                            M.cmd = "CATALOGUE"
                            M.value = [ 'PRO1', 'PRO2', 'PRO3' ]
                            self.log( "Sending catalogue %s" % msg.origine )
                            client.send(M)
            else:
                self.log("En attente de clients ... %s " % self.clients)
                time.sleep(1)

            ## ON ferme ?
            if not self.kill_q.empty():
                shutdown = self.kill_q.get()
                self.log( 'SHUTDOWN received ...' )

            time.sleep(1)
        self.log( "Fermeture " )
        return

## -------------
## Lancement 
## -------------
def compute():
    ## A revoir
    #BDD.init_base()

    ## Initialisation 
    processes = []
    clients = []
    kill_queue = multiprocessing.Queue()

    ## Creation de l'entreprise
    Ent = Entreprise( kill_queue )
    processes.append(Ent)
    ## Creation des clients
    nb_client = 5
    for n in range(nb_client):
        print "Creation client %s " % n
        ent_conn, cli_conn = multiprocessing.Pipe()
        #clients.append(ent_conn)
        Ent.add_client(ent_conn)
        c = Client(n, kill_queue, cli_conn)
        c.start()
        processes.append(c)
        time.sleep(1)
    Ent.start()
    ## Attente
    time.sleep(20)
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
