# -*- coding: utf-8 -*-

"""
Created on Mon 17/04/2017

@author: Miguel Diaz
"""

import psycopg2 as db

class dbman_pg:
    con = None
    cur = None
    sql = None
    def __init__(self,pg_host, pg_port, pg_user, pg_password, pg_database):
        self.con = db.connect(database=pg_database, user=pg_user, password=pg_password, host=pg_host, port=pg_port)
        self.cur = self.con.cursor()
        
        
    def insert(self, tabla, fields, values)    :
        if not fields:
            self.sql = "INSERT INTO {} VALUES ({});".format(tabla, values)        
        else:
            self.sql = "INSERT INTO {} ({}) VALUES ({});".format(tabla, fields, values)
            
        try:
            self.cur.execute(self.sql)
        except db.IntegrityError:
            return 0
        return 1        
        
    def select(self, tabla, where=False, fields=False):
        self.sql = "SELECT {} FROM {}"
        if where: self.sql += " WHERE {}"
        if fields:
            self.sql = self.sql.format(fields, tabla, where)
        else:
            self.sql = self.sql.format("*", tabla, where)
        self.sql += ";"
        self.cur.execute(self.sql)
        return self.cur.fetchall()
        
    def update(self, tabla,  set_value, where=False):        
        self.sql = "UPDATE {} SET {};"
        if where: self.sql = "UPDATE {} SET {} WHERE {};"
        self.sql = self.sql.format(tabla, set_value, where)
        self.cur.execute(self.sql)
        return self.cur.rowcount
        
    def delete(self, tabla, where):
        self.sql = "DELETE FROM {} WHERE {};"
        self.sql = self.sql.format(tabla, where)
        self.cur.execute(self.sql)
        return self.cur.rowcount
        
    def execute(self, sentence):
        self.sql = sentence
        self.cur.execute(self.sql)
        return self.cur.rowcount
    
    def execute_fetch(self, sentence):
        self.sql = sentence
        self.cur.execute(self.sql)
        return self.cur.fetchall()
        
    def end(self):
        self.con.close()
        
    def commit(self):
        self.con.commit()