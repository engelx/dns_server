#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 16:19:17 2017

@author: miguel
"""

import re, os

from handler_db_pg import dbman_pg as db_base

def getServers():
    path = "/".join(os.path.realpath(__file__).split("/")[:-1])+"/"
    file = open(path + "servers.conf", "r")
    server = file.read()
    servers = {}
    for serv in re.findall("(\w+)\:\{([\w\:\s\.]*)\}",server):
        temp = {}
        for val in re.findall("(\w+)\:\s*([\w\.]*)",serv[1]):
            temp[val[0]] = val[1]
        if len(temp)  != 5:
            return False
        servers[serv[0]] = temp
    file.close()
    return servers


localServer = getServers()["local"]
db = db_base(localServer["host"],localServer["port"],localServer["user"],localServer["pass"],localServer["dbname"]) #conexión

