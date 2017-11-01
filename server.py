#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@title           :MiniServerDNS
@author          :Engelx (Miguel A. Diaz)
@email           :mgldzm@gmail.com 
@date            :2017-08-31
@version         :0.7
@python_version  :3.5
"""
import re, os, time
from sys import exit
from threading import Thread
from handler_dns_query import dnsQuery
from handler_dns_query import dnsListener
from handler_db import dbman

        
def is_blocked(server, ip, host):
    if not host in server.blacklist: #si el servidor no está bloqueado
        return False
    
    if host in server.exceptions and ip in server.exceptions[host]: #si tiene el host libre
        return False
    
    if '%' in server.exceptions and ip in server.exceptions['%']: #si tiene el todo libre
        return False
    
    return True #está bloqueado

def get_cache(server, host):
    if host in server.cache: #si el host está en cache
        if server.cache[host].fixed: #si es un host fijo
            return server.cache[host].ip
        
        if server.cache[host].expire < time.time(): #si no está vencido
            return server.cache[host].ip
        else:
            del server.cache[host] # si está vencido se remueve
    
    return False
    
def set_cache(server, host, ip):
    server.cache["host"] = type('x', (object,), {
            "ip":ip, 
            "fixed":False, 
            "expire":time.time()+server.config.cache_expiration
            })
    
    
    

def dnsServer(listener, server, printSystem):
        request = listener.request
        client = listener.client
        query = dnsQuery(request)
        
        ##### Errores en el query #####
        if not query.host: #si el host está malformado o vacío
            if server.config.debug:
                printSystem.writeLog("dnsServer","No existe host a resolver, error")
            listener.send(client.pair, query.response()) 
            return False

            
        if not printSystem(client, query.host):# cargamos la ip
            return False
        
        filt = re.compile("^([\w\.\-])+$") # filtramos para evitar riesgos
        if not filt.match(query.host):
            if server.config.debug:
                printSystem.writeLog("dnsServer","Host invalido: {}".format(query.host))
            listener.send(client.pair, query.response()) #respondemos como invalido
            printSystem.ended(client)
            return False
        
        
        ##### Respuestas bloqueadas #####
        if server.config.use_block and is_blocked(server, client.ip, query.host): # si están activados los bloqueos y está blqoeiado
            if server.config.debug:
                    printSystem.writeLog("dnsServer","Host bloqueado ip: {:<16}, host:{}".format(client.ip, query.host))
            
            if server.config.data_display == 2: print(client.ip, client.port, query.host, server.config.redirect_blocked_ip)
            
            listener.send(client.pair, query.response(server.config.redirect_blocked_ip)) #respondemos con la ip del bloqueo
   
            if server.config.data_display == 2: print(client.ip, client.port, query.host, server.config.redirect_blocked_ip)
            if server.config.debug:
                pass #no implementado
                ##db.log(host, con.ip, config.redirect_blocked_ip) 
                
            printSystem.ended(client)
            return True
            
        ##### Respuestas no bloqueadas #####
        data = ""
        ip = get_cache(server, query.host)
        if not ip: #si no está en cache
            data = listener.forwardToDns(server.config.primary_dns, query.data, 2.0) 
            if not data: #si falla usamos el dns secundario
                data = listener.forwardToDns(server.config.secondary_dns, query.data, 2.0) 
            
            if not data: #si no hubo respuesta
                if server.config.debug:
                    printSystem.writeLog("dnsServer","Servidor remoto no respondió, host: {}".format(query.host))
                    
                listener.send(client.pair, query.response()) 
                printSystem.ended(client)
                return False
            
            ip = query.processResponse(data) # obtenemos la ip de la respuesta
            if not ip:
                listener.send(client.pair, query.response()) 
                printSystem.ended(client)
                return False
            
            set_cache(server, query.host, ip) # agregamos al cache
        
        listener.send(client.pair, query.response(ip)) 
        printSystem.ended(client)

        if server.config.data_display == 2: print(client.ip, client.port, query.host, ip)
        
        return True


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


class printSystem:
    def __init__(self, config):
        self.querys = {}
        self.count = 0
        self.log = config.log_file
        file = open(self.log, "a")
        if not file:
            msg = "No se pudo abrir el archivo de logs {}, saliendo del programa".format(self.log)
            self.printToScreen("ps",msg, "error", True)
            exit()
        
        if not self.writeLog("main","Servidor iniciado"):
            msg = "No se pudo imprimir en el archivo de logs {}, saliendo del programa".format(self.log)
            self.printToScreen("ps",msg, "error", True)
            exit()            
        file.close()
        
            
    def __call__(self, client, host):
        self.count += 1
        if client.ip in self.querys: # if the ip is in the query dict
            if client.port in self.querys[client.ip]: # if the port is already in user from that ip, is an error?
                self.writeLog("Query control", "ip: {}:{} is already in pool, duplicated query".format(client.ip,client.port))
                return False 
            
            self.querys[client.ip][client.port] = [host, time.time()] #show port in ip
            return True
        
        self.querys[client.ip] = {client.port: [host, time.time()]} #load ip with port -> host
        return True
        
    def ended(self, client):
        
        del self.querys[client.ip][client.port] # remove port
        
        if not len(self.querys[client.ip]): # remove ip
            del self.querys[client.ip]
    
    def __repr__(self):
        active = 0
        out = ""        
        for ip in self.querys:
            out += self._chColor("green")
            out += "{}:\n".format(ip)
            out += self._chColor("cyan")
            for port in self.querys[ip]:
                active += 1
                elapsed = time.time() - self.querys[ip][port][1]
                host = self.querys[ip][port][0]
                out += "{:-<6} {:<6}{:.2f} -> {}\n".format("", port, elapsed, host)
            out += self._chColor()
        return "Solicitudes activas: {}\n{}".format(active,out)
    
    def writeLog(self, system, msg):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        string = "{} [{}] - {}\n".format(timestamp, system, msg)
        file = open(self.log, "a")
        res = file.write(string)
        file.close()
        return res
        
    def printToScreen(self, system, msg, typemsg, clear=False):
        if clear: os.system("clear")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(timestamp, end=" ")
        
        
        print(self._chColor("green"), "{}".format(system),self._chColor(), end = " ")
        
        print("-".format(system), end = " ")
        
        if typemsg == "warning":
            print(self._chColor("yellow"), typemsg, self._chColor())            
        
        if typemsg == "error":
            print(self._chColor("red"), typemsg, self._chColor())                        
        
        if typemsg == "info":
            print(self._chColor("green"), typemsg, self._chColor())
            
        if typemsg == "debug":
            print(self._chColor("blue"), typemsg, self._chColor())
        
    def _chColor(self, color=False, bg=False):
        out = "\033[0m"
        if not bg:
            if color == "black": out = '\033[30m'
            if color == "red": out ='\033[31m'
            if color == "green": out ='\033[32m'
            if color == "orange": out ='\033[33m'
            if color == "blue": out ='\033[34m'
            if color == "purple": out ='\033[35m'
            if color == "cyan": out ='\033[36m'
            if color == "lightgrey": out ='\033[37m'
            if color == "darkgrey": out ='\033[90m'
            if color == "lightred": out ='\033[91m'
            if color == "lightgreen": out ='\033[92m'
            if color == "yellow": out ='\033[93m'
            if color == "lightblue": out ='\033[94m'
            if color == "pink": out ='\033[95m'
            if color == "lightcyan": out ='\033[96m'
        else:
            if color == "black": out ='\033[40m'
            if color == "red": out ='\033[41m'
            if color == "green": out ='\033[42m'
            if color == "orange": out ='\033[43m'
            if color == "blue": out ='\033[44m'
            if color == "purple": out ='\033[45m'
            if color == "cyan": out ='\033[46m'
            if color == "lightgrey": out ='\033[47m'
        return out
     

   
###############################################################################


localServer = getServers()["local"]
localdb = dbman(localServer)
server = type('x', (object,), {
        "blacklist":localdb.getBlacklist() , 
        "users":localdb.getUsers() , 
        "cache":localdb.getDomains(),
        "exceptions":localdb.getExceptions(),
        "config":localdb.getConfig()
        })

ps = printSystem(server.config) # print and log system

header = "Servidor iniciado: {}".format(time.strftime("%Y-%m-%d %H:%M:%S"))
os.system("clear")
print (header)
print ("Solicitudes:", ps.count) 

global running
running = True

listener = dnsListener()

try:
    while running: #until keyb interrupt
        
        if not listener.waitQuery(0.5):  #timout in 0.5 to actualize the display, on false restart
            continue
        
        thread = Thread(target = dnsServer, args = (listener, server, ps))
        thread.start()

        if server.config.data_display == 1:
            os.system("clear")
            print (header)
            print ("Servidor dns Principal:", server.config.primary_dns)
            print ("Servidor dns Principal:", server.config.secondary_dns)
            print ("Solicitudes:", ps.count) 
            print (ps)
        
except KeyboardInterrupt:
    running = False
    print ('Finalizando')











