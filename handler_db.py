#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 13:24:08 2017

@author: miguel
"""

from handler_db_pg import dbman_pg as db_base
import time

class dbman:
    def __init__(self):
        self.db = db_base("127.0.0.1","5432","postgres","1234","dns") #conection
        self.configuration = self.conf()
    
    def _conty(self, element): #convert from tring to bool or int
        if element.lower() == "true" or element.lower() == "false":
            return bool(element.lower() == "true")
        
        if element.isdigit():
            return int(element)
        
        return element
    
    def conf(self, element=False): #get configuration
        value = ""
        
        if element:
            value = self._conty(self.db.select("configuration", "name='{}'".format(element)))
        else:
            value = self.db.select("configuration")
            temp = {}
            for i in value:
                temp[i[0]]= self._conty(i[1])
            value = temp
        return value
    
    def blocked(self, host, ip): #is host blocked for this ip
        value = self.db.select("exceptions","('.{}' like host or host='ALL') and ip='{}'".format(host, ip))
        if value:
            return False
        
        value = self.db.select("blacklist","'.{}' like host".format(host))
        if value:
            return True
        
        return False
        
    def cache(self, host): #chech if ip is cached
        value = self.db.select("cache", "host='{}'".format(host),"ip,fixed,expire")
        if not value:
            return False
        
        ip, fixed, expire = value[0]
        
        if self._conty(fixed):
            return ip
        
        if self._conty(expire)+self.configuration["cache_expiration"] > int(time.time()):
            return ip 
        else:
            self.db.delete("cache", "host='{}'".format(host))
            self.db.commit()
            return False
        
        return False

    def log(self, host, ip, answer):
        fields = "id, ip, date, host, answer"
        date = time.strftime("%Y-%m-%d %H:%M:%S")
        values = "(select count(id)+1 from logs), '{}', '{}', '{}', '{}'".format(ip,date,host,answer)
        self.db.insert("logs",fields, values)
        self.db.commit()