#!/usr/bin/env python
# -*- coding: utf-8 -*- 


import multiprocessing
import initialisation
import sqlite3
import random
import time
import os, sys

BASE_FILE = "test.dbf"

processes = []

def log(msg, f):
    #print >> f, msg
    f.write(msg)
    f.flush()

def client_process(cli_number, kill_queue, Ent_conn):

    kill_flag = False

    while not kill_flag:
        while Ent_conn.poll():
            print 'Process %s received message: %s' % (cli_number, Ent_conn.recv())
            ## On traite le message
            Ent_conn.send(" Message recu  %s " % cli_number )

        ## Si pas de message
        if random.choice(range(100)) > 50:
            Ent_conn.send('Client : %s envoi de commande' % cli_number)
        else:
            sleep_time = 5
            print 'Client %s en attente' % cli_number
            time.sleep(sleep_time)

        ## Si Kill Flag on arrete
        if not kill_queue.empty():
            kill_flag = kill_queue.get()
            print 'KILL FLAG => %s' % cli_number

def ent_process(nb_client, fic,  kill_q):
    log( "Ouverture", fic)
    clients = []
    kill_queue = multiprocessing.Queue()

    ## Initialisation 
    ## Creation des clients
    for number in range(nb_client):
        ent_connexion, cli_connexion = multiprocessing.Pipe()
        clients.append(ent_connexion)
        process = multiprocessing.Process(target=client_process, args=(number,kill_queue,cli_connexion,))
        process.start()
        processes.append(process)

    # Les clients sont crées
    ## On transmets le catalogue
    for number, client in enumerate(clients):
        client.send('Envoi du Catalogue : %s' % number)

    ## On attend un peu
    t = 10
    log( "MAIN SLEEP : %s " % t, fic)
    time.sleep(t)

    ## Boucle principale
    shutdown = False

    while not shutdown:
        for client in clients:
            while client.poll():
                print 'Recu du client : %s' % client.recv()

        ## ON ferme ?
        if not kill_queue.empty():
            shutdown = kill_q.get()
            print 'SHUTDOWN ...'

    ## Fermeture des processes
    for process in processes:
        kill_queue.put(True)
                    
    for process in processes:
        process.join()
    log( "Fermeture ...", fic)

## -------------
## Lancement 
## -------------
def run():
    #initialisation.init_base()
    kill_q = multiprocessing.Queue()
    fic_log = open( "out.log", 'w' )
    p = multiprocessing.Process(target=ent_process, args=(5, fic_log, kill_q,))
    time.sleep(10)
    ## On ferme
    kill_q.put(True)

## ---------------
## Main
## ---------------
if __name__ == '__main__':
    run()
