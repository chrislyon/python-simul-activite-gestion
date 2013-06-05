import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

con = sqlite3.connect(":memory:")
con.row_factory = dict_factory
cur = con.cursor()
cur.execute(" create table TOTO ( ID integer, CODE VARCHAR(10) );")
con.commit()
cur.execute(" insert into TOTO VALUES (1, 'C1');")
cur.execute(" insert into TOTO VALUES (2, 'C2');")
cur.execute(" insert into TOTO VALUES (3, 'C3');")
cur.execute(" insert into TOTO VALUES (4, 'C4');")
con.commit()

cur.execute("select * from TOTO where ID=2;")
d = cur.fetchone()
print "d[ID]=", d["ID"]
print "d[CODE]=", d["CODE"]

con.row_factory = None
cur = con.cursor()
cur.execute("select * from TOTO where ID=2;")
d = cur.fetchone()
print d
