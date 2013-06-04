#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sqlite3
import os

## ---------------------------------
## Creation de la base de données
## ---------------------------------
def create_base( BASE_FILE ):
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

class BDD():
    def __init__(self, FIC_BASE):
        #ouverture de la base
        self.conn = sqlite3.connect(FIC_BASE)

    def get_param(self, param_name):
        c = self.conn.cursor()
        c.execute("select CODPAR, TYP, VALUE from PARAM where CODPAR='%s';" % param_name)
        data = c.fetchone()
        if data:
            t = data[1]
            v = data[2]
            if t == 1:  ## int
                return int(v)
            elif t == 2:    ## String
                return v
        else:
            return None

def test():
    F = 'test.dbf'
    create_base(F)
    BASE = BDD(F)
    ## Test get_param
    print "NB_PRODUIT = ", BASE.get_param('NB_PRODUIT')
    print "Inexistant = ", BASE.get_param('inexistant')

if __name__ == '__main__':
    test()
