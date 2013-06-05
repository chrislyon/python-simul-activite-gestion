#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sqlite3
import os

## ---------------------------------
## Creation de la base de données
## ---------------------------------
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

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
    COMCLI_START = 1000


    ## Parametre
    REQ = "CREATE TABLE PARAM ( CODPAR VARCHAR(20) , TYP INTEGER, VALUE TEXT);"
    c.execute(REQ)
    REQ = "INSERT INTO PARAM VALUES ( 'NB_PRODUIT', 1, '%s');" % NB_PRODUIT
    c.execute(REQ)
    REQ = "INSERT INTO PARAM VALUES ( 'NB_CLIENT', 1, '%s');" % NB_CLIENT
    c.execute(REQ)
    REQ = "INSERT INTO PARAM VALUES ( 'NB_FOU', 1, '%s');" % NB_FOU
    c.execute(REQ)
    REQ = "INSERT INTO PARAM VALUES ( 'COUNTER_COMCLI', 1, '%s');" % COMCLI_START
    c.execute(REQ)

    ## Table produits
    REQ = "CREATE TABLE PRODUITS ( CODE VARCHAR(15), NOM VARCHAR(30), PRIX NUMBER(9.2), STOCK NUMBER(9) );"
    c.execute(REQ)
    for x in xrange(1, NB_PRODUIT+1):
        p_name = "PRO%04d" % x
        c.execute(" INSERT INTO PRODUITS VALUES ( '%s', 'Designation produit %s', 100, 0);" % (p_name, p_name) )

    ## Table clients
    REQ = "CREATE TABLE CLIENTS ( CODE VARCHAR(15), NOM VARCHAR(30), ADRESSE TEXT, CODPOS VARCHAR(10), VILLE VARCHAR(30) );"
    c.execute(REQ)
    for x in xrange(1, NB_CLIENT+1):
        c_code = "CLI%04d" % x
        c_nom = "Ste %s SARL" % c_code
        c_adr = "Rue de la republique"
        c_cp = "01%03d" % x
        c_ville = "JOLIE VILLE"
        c.execute(" INSERT INTO CLIENTS VALUES ( '%s', '%s', '%s', '%s', '%s');" % (c_code, c_nom, c_adr, c_cp, c_ville) )

    ## Table Fou
    REQ = "CREATE TABLE FOURN ( CODE VARCHAR(15), NOM VARCHAR(30), ADRESSE TEXT, CODPOS VARCHAR(10), VILLE VARCHAR(30) );"
    c.execute(REQ)
    for x in xrange(1, NB_FOU+1):
        f_code = "FOU%04d" % x
        f_nom = "Ste %s SARL" % f_code
        f_adr = "Rue des fournisseurs"
        f_cp = "02%03d" % x
        f_ville = "PETITE VILLE"
        c.execute(" INSERT INTO FOURN VALUES ( '%s', '%s', '%s', '%s', '%s');" % (f_code, f_nom, f_adr, f_cp, f_ville) )

    ## Table Commande Client 
    REQ = "CREATE TABLE COMCLI ( NUMCOM INTEGER, CODCLI VARCHAR(15) , NOMCLI VARCHAR(30), ADRCLI TEXT, CP VARCHAR(10), VILLE VARCHAR(30) );"
    c.execute(REQ)
    REQ = "CREATE TABLE LIGCLI ( NUMCOM INTEGER , NUMLIG INTEGER,  CODPRO VARCHAR(15), COMMENT TEXT, QTE INTEGER, PRIX NUMBER(9.2) );"
    c.execute(REQ)

    ## Fin
    conn.commit()
    conn.close()

class LIGCLI():
    def __init__(self, PRO, lig):
        self.NUMCOM = 0
        self.NUMLIG = lig
        self.CODPRO = PRO
        self.COMMENT = ""
        self.QTE = 0
        self.PRIX = 0

    def to_sql(self):
        r = "insert into LIGCLI values ("
        r += "%s, %s, '%s', '%s', %s, %s" % ( self.NUMCOM, self.NUMLIG, self.CODPRO, self.COMMENT, self.QTE, self.PRIX )
        r += ");"
        return r

class COMCLI():
    def __init__(self, cli):
        self.NUMCOM = 0
        self.CODCLI = cli
        self.NOMCLI = ""
        self.ADRCLI = ""
        self.CP = ""
        self.VILLE = ""
        self.lignes = []

    def to_sql(self):
        R = []
        ## Entete
        r = "insert into COMCLI values (" 
        r += "%s, '%s', '%s', '%s', '%s', '%s'" % (self.NUMCOM, self.CODCLI, self.NOMCLI, self.ADRCLI, self.CP, self.VILLE)
        r += ");"
        R.append(r)
        ## Lignes
        for l in self.lignes:
            l.NUMCOM = self.NUMCOM
            R.append(l.to_sql())
        return R

class BDD():
    def __init__(self, FIC_BASE):
        #ouverture de la base
        self.conn = sqlite3.connect(FIC_BASE)

    def set_param(self, p_name, value ):
        c = self.conn.cursor()
        c.execute("update PARAM set VALUE='%s' where CODPAR='%s';" % (value, p_name) )
        self.conn.commit()
        return True

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

    def get_catalogue(self, critere=None):
        c = self.conn.cursor()
        c.execute("select CODE from PRODUITS;")
        data = c.fetchall()
        ## Je veu pas ds tuples mais une liste
        return [ d[0] for d in data ]
    
    def look(self, table, cle):
        c = self.conn.cursor()
        c.execute("select CODE from %s where CODE='%s';" % (table, cle))
        data = c.fetchone()
        if data:
            return data[0]
        else:
            return None

    def read(self, table, cle, champ="CODE"):
        OLD_rf = self.conn.row_factory
        self.conn.row_factory = dict_factory
        c = self.conn.cursor()
        c.execute("select * from %s where %s='%s';" % (table, champ, cle))
        data = c.fetchone()
        self.conn.row_factory = OLD_rf
        if data:
            return data
        else:
            return None

    def counter_next_val(self, COUNTER):
        C_NAME = "COUNTER_%s" % COUNTER
        counter = self.get_param( C_NAME )
        counter += 1
        if counter:
            self.set_param( C_NAME, counter )
        return counter

    def create_COMCLI(self, cli, lignes):
        OK = True
        NUMCOM = None
        # Verification du client
        CLIENT = self.read("CLIENTS", cli)
        if CLIENT:
            CMD = COMCLI(CLIENT["CODE"])
            CMD.NOMCLI = CLIENT["NOM"]
            CMD.ADRCLI = CLIENT["ADRESSE"]
            CMD.CP = CLIENT["CODPOS"]
            CMD.VILLE = CLIENT["VILLE"]
            # Pour toutes les lignes
            nl = 0
            for l in lignes:
                ## Verif du produit
                PRODUIT = self.read("PRODUITS", l[0])
                if PRODUIT:
                    ## creation de la ligne
                    nl += 1
                    LIG = LIGCLI( PRODUIT["CODE"], nl )
                    LIG.QTE = l[1]
                    LIG.COMMENT = PRODUIT["NOM"]
                    LIG.PRIX = PRODUIT["PRIX"]
                    CMD.lignes.append(LIG)
                else:
                    ## Erreur produit inexistant
                    OK = False
            # ON peut aller chercher le numero de commande
            if OK:
                CMD.NUMCOM = self.counter_next_val('COMCLI')
                NUMCOM = CMD.NUMCOM
                # on valide
                c = self.conn.cursor()
                REQS = CMD.to_sql()
                for REQ in REQS:
                    c.execute(REQ)
                self.conn.commit()
        return NUMCOM


def test():
    F = 'test.dbf'
    create_base(F)
    BASE = BDD(F)
    ## Test get_param
    print "NB_PRODUIT = ", BASE.get_param('NB_PRODUIT')
    print "Inexistant = ", BASE.get_param('inexistant')
    ## Get catalogue
    print BASE.get_catalogue()
    ## Test look
    print BASE.look("CLIENTS", "CLI0001")
    print BASE.look("PRODUITS", "NONAME")
    ## Test read
    print BASE.read("CLIENTS", "CLI0002")
    print BASE.read("PRODUITS", "PRO0003")
    ## Test set_param
    print "SET PARAM = ", BASE.set_param("COUNTER_COMCLI", 1001)
    print "SET PARAM = ", BASE.get_param("COUNTER_COMCLI")
    ## Test counter_next_val
    print "Counter next_val = ", BASE.counter_next_val('COMCLI')
    ## Test create_COMCLI
    print "create COMCLI = ", BASE.create_COMCLI( "CLI0003", [ ('PRO0001', 5), ('PRO0002', 10), ('PRO0003', 15) ] )



if __name__ == '__main__':
    test()
