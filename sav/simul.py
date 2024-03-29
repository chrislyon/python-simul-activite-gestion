#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from multiprocessing import Process, Manager
import sqlite3
import os

BASE_FILE = "test.dbf"

class Message():
    def __init__(self):
        self.ref_int = ""
        self.ref_ext = ""
        self.objet = ""
        self.status = None
        self.contenu = None

## ---------------
## Classe Client
## ---------------
class Client(Process):
    """
        Classe Client : son role est de generer des commandes
    """
    def __init__(self, name, Ent_q):
        super(Client, self).__init__()
        self.name = name
        self.cde = Ent_q

    def run(self):
        print "Client : %s " % self.name
        ## Ici le client
        ## On recupere le catalogue
        M = Message()
        M.ref_int = "CATALOG"
        M.objet = "CATALOG"
        self.cde.put(M)
        cat = self.cde.wait()
        ## et passe une commande
        print cat

class Entreprise(Process):
    def __init__(self, name, Ent_q):
        super(Client, self).__init__()
        self.name = name
        self.cde = Ent_q


## ---------------------------------
## Creation de la base de données
## ---------------------------------
def init_base():
    try:
        os.remove( BASE_FILE )
    except:
        print "INIT_BASE : Fichier %s inexistant " % BASE_FILE
        pass
    ## Initialisation de la BDD
    conn = sqlite3.connect(BASE_FILE)
    c = conn.cursor()
    ## Init Dictionnaire
    NB_PRODUIT = 10
    NB_CLIENT = 10
    NB_FOU = 5


    ## Parametre
    REQ = "CREATE TABLE PARAM ( CODPAR VARCHAR(20) , TYP INTEGER, VALUE TEXT);"
    c.execute(REQ)
    REQ = "INSERT INTO PARAM VALUES ( 'NB_PRODUIT', 1, '%s');" % NB_PRODUIT
    c.execute(REQ)
    REQ = "INSERT INTO PARAM VALUES ( 'NB_CLIENT', 1, '%s');" % NB_CLIENT
    c.execute(REQ)
    REQ = "INSERT INTO PARAM VALUES ( 'NB_FOU', 1, '%s');" % NB_FOU
    c.execute(REQ)

    ## Table produits
    REQ = "CREATE TABLE PRODUITS ( CODPRO VARCHAR(15), DESIG VARCHAR(30), PRIX NUMBER(9.2), STOCK NUMBER(9) );"
    c.execute(REQ)
    for x in xrange(1, NB_PRODUIT+1):
        p_name = "PRO%04d" % x
        c.execute(" INSERT INTO PRODUITS VALUES ( '%s', 'Designation produit %s', 100, 0);" % (p_name, p_name) )

    ## Table clients
    REQ = "CREATE TABLE CLIENTS ( CODCLI VARCHAR(15), NOM VARCHAR(30), ADRESSE TEXT, CODPOS VARCHAR(10), VILLE VARCHAR(30) );"
    c.execute(REQ)
    for x in xrange(1, NB_CLIENT+1):
        c_code = "CLI%04d" % x
        c_nom = "Ste %s SARL" % c_code
        c_adr = "Rue de la republique"
        c_cp = "01%03d" % x
        c_ville = "JOLIE VILLE"
        c.execute(" INSERT INTO CLIENTS VALUES ( '%s', '%s', '%s', '%s', '%s');" % (c_code, c_nom, c_adr, c_cp, c_ville) )

    ## Table Fou
    REQ = "CREATE TABLE FOURN ( CODFOU VARCHAR(15), NOM VARCHAR(30), ADRESSE TEXT, CODPOS VARCHAR(10), VILLE VARCHAR(30) );"
    c.execute(REQ)
    for x in xrange(1, NB_FOU+1):
        f_code = "FOU%04d" % x
        f_nom = "Ste %s SARL" % f_code
        f_adr = "Rue des fournisseurs"
        f_cp = "02%03d" % x
        f_ville = "PETITE VILLE"
        c.execute(" INSERT INTO FOURN VALUES ( '%s', '%s', '%s', '%s', '%s');" % (f_code, f_nom, f_adr, f_cp, f_ville) )

    ## Fin
    conn.commit()
    conn.close()


def lance_clients(nb):
    for c in xrange(0,nb):
        p = Client("CLI%04d" % c)
        p.start()
        p.join()

## -------------
## Lancement 
## -------------
def run():
    init_base()
    Ent = Entreprise( BASE_FILE )
    #lance_clients(5, Ent)

## ---------------
## Main
## ---------------
if __name__ == '__main__':
    run()
