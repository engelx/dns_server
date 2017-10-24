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
import socket #socket related
import re, os, time
from sys import exit
from threading import Thread
import handler_dns_query as hdnsq
from handler_db import dbman


def forwardQueryToDNS(data, conf, ps, dns="primary_dns"):
    forward = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    forward.settimeout(3) # 3 second timout
    forward.connect((conf[dns], 53)) #call to the dns server
    forward.send(hdnsq.IntToByte(data)) # send data in bytes
    try: #if no timeout
        return hdnsq.processResponse(forward.recv(512)) #get answer
    except socket.timeout: #if timeout
        ps.writeLog("dnsServer", "El servidor {} {} no respondió".format(dns, conf[dns]))
        if dns == "primary_dns":
            return forwardQueryToDNS(data, conf, ps, dns="secondary_dns")
        else:
            return False

def dnsServer(data, ip, conf, udps, ps, server):
        sender = udps
        data, host = hdnsq.processQuery(data)
        
        if not host:
            if conf["debug"]: 
                ps.writeLog("dnsServer","No existe host a resolver: \n data.\n {}".format(data))

            data = hdnsq.generateResponse(data) # we cannot resolve this
            sender.sendto(data, ip)
            
            return False
        
        if not ps(ip,host):# load into pool
            return False
        
        filt = re.compile("^([\w\.\-])+$") # filter to aviod risks, 
        if not filt.match(host):
            if conf["debug"]:
                ps.writeLog("dnsServer","Host invalido: {}".format(host))

            data = hdnsq.generateResponse(data) # we cannot resolve this
            sender.sendto(data, ip)
            ps.ended(ip)
            return False
          
        db = dbman(server)
        
        if db.blocked(host, ip[0]) and conf["use_block"]:  # if is blacked and we are blocking
            if conf["debug"]:
                    ps.writeLog("dnsServer","Host bloqueado ip: {:<16}, host:{}".format(ip[0], host))
            data = hdnsq.generateResponse(data, conf["redirect_blocked_ip"]) # blocker ip
            if conf["data_display"] == 2: print(ip[0],ip[1],host, conf["redirect_blocked_ip"])
            sender.sendto(data, ip)
            if conf["debug"]:
                db.log(host, ip[0], conf["redirect_blocked_ip"]) 
            ps.ended(ip)
            return True
        
        answer = db.cache(host)
        
        if not answer: # if no in cache
            answer = forwardQueryToDNS(data, conf, ps)
            if not answer: #if not in dns server or conection problem
                if conf["debug"]:
                    ps.writeLog("dnsServer","Servidor remoto no respondió, host: {}".format(host))
                data = hdnsq.generateResponse(data) # we cannot resolve this
                sender.sendto(data, ip)
                ps.ended(ip)
                return False            
            db.cache(host, answer)
            
        if conf["debug"]:
            db.log(host, ip[0], answer) 
        data = hdnsq.generateResponse(data, answer) # blocker ip     
        
        if conf["data_display"] == 2: print(ip[0],ip[1],host, answer)
        
        
        sender.sendto(data, ip)
        ps.ended(ip)
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
    def __init__(self, conf):
        self.querys = {}
        self.count = 0
        self.log = conf["log_file"]
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
        
            
    def __call__(self, ipPort, host):
        ip = ipPort[0]
        port = ipPort[1]
        self.count += 1
        if ip in self.querys: # if the ip is in the query dict
            if port in self.querys[ip]: # if the port is already in user from that ip, is an error?
                self.writeLog("Query control", "ip: {}:{} is already in pool, duplicated query".format(ip,port))
                return False 
            
            self.querys[ip][port] = [host, time.time()] #show port in ip
            return True
        
        self.querys[ip] = {port: [host, time.time()]} #load ip with port -> host
        return True
        
    def ended(self, ipPort):
        ip = ipPort[0]
        port = ipPort[1]
        
        del self.querys[ip][port] # remove port
        
        if not len(self.querys[ip]): # remove ip
            del self.querys[ip]
    
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
config = localdb.getConfig()

ps = printSystem(config) # print and log system

header = "Servidor iniciado: {}".format(time.strftime("%Y-%m-%d %H:%M:%S"))
os.system("clear")
print (header)
print ("Solicitudes:", ps.count) 

global running
running = True
udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # open listen socket
udps.bind(('',53)) # as port 53, DNS

last_time = time.time() #countdown to reload conf


try:
    while running: #forever
        try:
            udps.settimeout(0.5)#timout in 0.5 to actualize the display
            data, ip = udps.recvfrom(512) #read packet
            thread = Thread(target = dnsServer, args = (data, ip, config, udps, ps, localServer))
            thread.start()
        except socket.timeout:
            pass
        
        config = localdb.getConfig()
        
        if config["data_display"] == 1:
            os.system("clear")
            print (header)
            print ("Servidor dns Principal:", config["primary_dns"])
            print ("Servidor dns Principal:", config["secondary_dns"])
            print ("Solicitudes:", ps.count) 
            print (ps)
        
except KeyboardInterrupt:
    running = False
    print ('Finalizando')




















