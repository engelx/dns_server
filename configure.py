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
import sys, re
from handler_db import dbman

def chColor(color=False, bg=False):
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


def showHelp():
    _no = chColor()
    _bl = chColor("lightblue")
    _cy = chColor("cyan")
    _gr = chColor("green")
    _ye = chColor("yellow")
    _re = chColor("lightred")
    _pu = chColor("pink")
    out = "Ayuda:\n"
    
    filename = "configure.py"
    
    #out += _ye + filename + _gr + " user " + _bl + "add \n" + _no
    #out += "  Inicia el menú para añadir un usuario\n"
    out += _ye + filename + _bl + " user " + _gr + "add " + _cy + "{username} {group} {ip}  \n" + _no
    out += "  Agrega un usuario\n"
    out += _ye + filename + _bl + "u ser " + _re + "rem user " + _cy + "{username}\n" + _no
    out += "  Elimina un usuario\n"
    out += _ye + filename + _bl + " user " + _re + "rem group " + _cy + "{group}\n" + _no
    out += "  Elimina todos los usuarios de un grupo y el grupo\n"
    out += _ye + filename + _bl + " user " + _pu + "check "  + _cy + "[group]\n" + _no
    out += "  Imprime en un archivo toda la información sobre los usuarios, si grupo no es usado, se mostrarán todos\n\n"
    
    #out += _ye + filename + _gr + " except " + _bl + "add \n" + _no
    #out += "  Inicia el menú para añadir excepciones\n"
    out += _ye + filename + _bl + " except " + _gr + "add user " + _cy + "{username} [host]\n" + _no
    out += "  Agrega una excepción para un usuario, si no use usa host, se libera todo\n"
    out += _ye + filename + _bl + " except " + _re + "rem user " + _cy + "{username} [host]\n" + _no
    out += "  Elimina una excepción de un usuario, si no se usa host, se eliminan todas\n"
    out += _ye + filename + _bl + " except " + _gr + "add group " + _cy + "{group} [host]\n" + _no
    out += "  Agrega una excepción para un grupo, si no use usa host, se libera todo\n"
    out += _ye + filename + _bl + " except " + _re + "rem group " + _cy + "{group} [host]\n" + _no
    out += "  Elimina una excepción de un grupo, si no se usa host, se eliminan todas\n"
    out += _ye + filename + _bl + " except " + _pu + "check " + _cy + "[grupo] \n" + _no
    out += "  Muestra toda la información sobre las excepciones de bloqueo,\n  si no se usa un un grupo se imprimirá todo\n\n"
      
    #out += _ye + filename + _gr + " blocked " + _bl + "add \n" + _no
    #out += "  Inicia el menú para añadir un bloqueo\n"
    out += _ye + filename + _bl + " blocked " + _gr + "add " + _cy + "{host} {category}\n" + _no
    out += "  Agrega un host a bloquear\n"
    out += _ye + filename + _bl + " blocked " + _re + "rem host " + _cy + "{host}\n" + _no
    out += "  Elimina todos los host de una categoría\n"
    out += _ye + filename + _bl + " blocked " + _re + "rem cat " + _cy + "{category}\n" + _no
    out += "  Elimina un host bloqueado\n"
    out += _ye + filename + _bl + " blocked " + _pu + "check " + _cy + "[category] \n" + _no
    out += "  Muestra toda la información sobre los host bloqueados,\n  si no se usa una categoría se imprimirá todo\n\n"
    
    #out += _ye + filename + _gr + " domain " + _bl + "add \n" + _no
    #out += "  Inicia el menú para añadir un dominio\n"
    out += _ye + filename + _bl + " domain " + _gr + "add " + _cy + "{host} {ip}\n" + _no
    out += "  Asigna crea un dominio con ip fija\n"
    out += _ye + filename + _bl + " domain " + _re + "rem " + _cy + "{host}\n" + _no
    out += "  Libera a un dominio\n"
    out += _ye + filename + _bl + " domain " + _pu + "check \n" + _no
    out += "  Imprime en un archivo toda la información sobre los dominios creados\n\n"
    
    out += _ye + filename + _bl + " configuration " + _pu + "check \n" + _no
    out += "  Muestra la configuración del servidor\n"
    out += _ye + filename + _bl + " configuration " + _pu + "mod " + _cy + "{field} {value}\n" + _no
    out += "  Modifica un valor de la configuración\n"
    
    print(out)

def getServers():
    file = open("servers.conf", "r")
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

def printLs(server_name, header,ls):
    space = []
    for word in header:
        space.append(len(word))
    for l in ls:
        
        for s in range(len(space)):
            if len(l[s]) > space[s]: space[s] = len(l[s])
    temp = 0
    string = "|"
    for s in range(len(space)):
        space[s] += 2
        temp+=space[s]
        string += "{:^{}}|".format(header[s],space[s])
        
        
    space.append(temp+2)
    print("-"*(space[-1]+2))
    print("| {:<{}}|".format("{}:{}".format("SERVIDOR",server_name) ,space[-1]-1))
    print("|{:-<{}}|".format("", space[-1]))
    print(string)
    
    for el in ls:
        string = "|"
        for s in range(len(space)-1):
            string += "{:^{}}|".format(el[s],space[s])
        print(string)
    print("-"*(space[-1]+2))

def userAdd(name, group, ip):
    if not re.match("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", ip):
        print("Error, ip invalida")
        return
    servers = getServers()
    for server_name in servers:
        server = servers[server_name]
        db = dbman(server)
        affected = db.userAdd(name, group, ip)
        if affected:
            print("Agregado el registro: {}@{} en grupo {} en el servidor {}".format(name.upper(), ip, group.upper(), server_name))
        else:
            print("Error al agregar")

def userRem(name, group=False):
    servers = getServers()
    for server_name in servers:
        server = servers[server_name]
        db = dbman(server)
        affected = 0
        affected = db.userRem(name, group)
        print("Eliminados", affected,"registros en servidor",server_name)
        
def userCheck(group=False):
    servers = getServers()
    for server_name in servers:
        server = servers[server_name]
        db = dbman(server)
        ls = db.userCheck(group)
        printLs(server_name, ["NOMBRE", "IP", "GRUPO"], ls)
        
def exceptionAdd(name, host=False, group=False):
    servers = getServers()
    for server_name in servers:
        server = servers[server_name]
        db = dbman(server)
        affected = db.exceptionAdd(name, host, group)
        print("Agregadas",affected,"registros en el servidor",server_name)
        
def exceptionRem(name, host=False, group=False):
    servers = getServers()
    for server_name in servers:
        server = servers[server_name]
        db = dbman(server)
        affected = db.exceptionRem(name, host, group)
        print("Eliminados", affected,"registros en servidor",server_name)
        
                
def exceptionCheck(user=False, group=False):
    servers = getServers()
    for server_name in servers:
        server = servers[server_name]
        db = dbman(server)
        ls = db.exceptionCheck(user, group)
        printLs(server_name, ["NOMBRE",  "IP", "HOST"], ls)
              
def blockAdd(host, cat):
    servers = getServers()
    for server_name in servers:
        server = servers[server_name]
        db = dbman(server)
        affected = db.blockAdd(host, cat)
        print("Agregadas",affected,"registros en el servidor",server_name)

def blockRem(host, cat=False):
    servers = getServers()
    for server_name in servers:
        server = servers[server_name]
        db = dbman(server)
        affected = db.blockRem(host,cat)
        print("Eliminados", affected,"registros en servidor",server_name)

def blockCheck(cat=False):
    servers = getServers()
    for server_name in servers:
        server = servers[server_name]
        db = dbman(server)
        ls = db.blockCheck(cat)
        printLs(server_name, ["HOST",  "CATEGORIA"], ls)

def cacheStaticAdd(host, ip):
    servers = getServers()
    for server_name in servers:
        server = servers[server_name]
        db = dbman(server)
        affected = db.cacheStaticAdd(host, ip)
        print("Agregadas",affected,"registros en el servidor",server_name)

def cacheStaticRem(host):
    servers = getServers()
    for server_name in servers:
        server = servers[server_name]
        db = dbman(server)
        affected = db.cacheStaticRem(host)
        print("Eliminados",affected,"registros en el servidor",server_name)

def cacheStaticCheck():
    servers = getServers()
    for server_name in servers:
        server = servers[server_name]
        db = dbman(server)
        ls = db.cacheStaticCheck()
        printLs(server_name, ["HOST",  "IP"], ls)
        
def configurationModify(field, value):
    servers = getServers()
    for server_name in servers:
        server = servers[server_name]
        db = dbman(server)
        affected = db.configurationModify(field, value)
        print("Madificados",affected,"registros en el servidor",server_name)

def configurationCheck():
    servers = getServers()
    for server_name in servers:
        server = servers[server_name]
        db = dbman(server)
        ls = db.configurationCheck()
        printLs(server_name, ["CAMPO",  "VALOR"], ls)

###########################################################################    



def menu(params):
    ### USUARIOS ###
    if params[0].lower() == "user":
        params=params[1:]
        
        ### AGREGAR ###
        if params[0].lower() == "add":
            params=params[1:]
            if len(params) != 3 :return False
            userAdd(params[0], params[1], params[2])
            return True

        ### ELIMINAR ###
        elif params[0].lower() == "rem":
            params=params[1:]
            
            ### USUARIO ###
            if params[0].lower() == "user":
                params=params[1:]
                if len(params) != 1 :return False
                userRem(params[0])
                return True
                
            ### GRUPO ###
            elif params[0].lower() == "group":
                params=params[1:]
                if len(params) != 1 :return False
                userRem(params[0], True)
                return True
            else:
                return False
        
        ### LISTAR ###
        elif params[0].lower() == "check":
            params=params[1:]
            if len(params) == 0 :
                userCheck()
                return True
            elif len(params) == 1 :
                userCheck(params[0])
                return True
            else:
                return False
        else:
            return False
    
    ### EXCEPCIONES ###
    elif params[0] == "except":
        params=params[1:]
        
        ### AGREGAR ###
        if params[0].lower() == "add":
            params=params[1:]
            
            ### USUARIO ###
            if params[0].lower() == "user":
                params=params[1:]
                if len(params) == 1:
                    exceptionAdd(params[0])
                    return True
                elif len(params) == 2:
                    exceptionAdd(params[0], params[1])
                    return True
                else:
                    return False
                
            ### GRUPO ###
            elif params[0].lower() == "group":
                params=params[1:]
                if len(params) == 1:
                    exceptionAdd(params[0], False, True)
                    return True
                elif len(params) == 2:
                    exceptionAdd(params[0], params[1], True)
                    return True
                else:
                    return False
            
            else:
                return False

        ### ELIMINAR ###    
        elif params[0].lower() == "rem":
            params=params[1:]
            
            ### USUARIO ###
            if params[0].lower() == "user":
                params=params[1:]
                if len(params) == 1:
                    exceptionRem(params[0])
                    return True
                elif len(params) == 2:
                    exceptionRem(params[0], params[1])
                    return True
                else:
                    return False
                
            ### GRUPO ###
            elif params[0].lower() == "group":
                params=params[1:]
                if len(params) == 1:
                    exceptionRem(params[0], False, True)
                    return True
                elif len(params) == 2:
                    exceptionRem(params[0], params[1], True)
                    return True
                else:
                    return False
                
            else:
                return False

        ### LISTAR ###
        elif params[0].lower() == "check":
            params=params[1:]
            if len(params) == 0:
                exceptionCheck()
                return True
            elif len(params) == 1:
                exceptionRem(params[0], True)
                return True
            else:
                return False
        else:
            return False
        
        
    ### BLOQUEADOS ###
    elif params[0] == "blocked":
        params=params[1:]
 
        ### AGREGAR ###
        if params[0].lower() == "add":
            params=params[1:]
            if len(params) == 2:
                blockAdd(params[0], params[1])
                return True
            else:
                return False

        ### ELIMINAR ###    
        elif params[0].lower() == "rem":
            params=params[1:]
            
            ### HOST ###
            if params[0].lower() == "host":
                params=params[1:]
                if len(params) == 1:
                    blockRem(params[0])  
                    return True
                else:
                    return False
            ### CATEGORIA ###
            elif params[0].lower() == "cat":
                params=params[1:]     
                if len(params) == 1:
                    blockRem(params[0], True)  
                    return True
                else:
                    return False
            
            else:
                return False
            
        ### LISTAR ###
        elif params[0].lower() == "check":
            params=params[1:]
            if len(params) == 0:
                blockCheck()
                return True
            elif len(params) == 1:
                blockCheck(params[0], True)
                return True
            else:
                return False
            
        else:
            return False
            
            
    ### CACHE ESTATICOS ###
    elif params[0] == "domain":
        params=params[1:]

        ### AGREGAR ###
        if params[0].lower() == "add":
            params=params[1:]
            if len(params) == 2:
                cacheStaticAdd(params[0], params[1])
                return True
            else:
                return False
            
        ### ELIMINAR ###    
        elif params[0].lower() == "rem":
            params=params[1:]
            if len(params) == 1:
                cacheStaticRem(params[0])
                return True
            else:
                return False
            
        ### LISTAR ###
        elif params[0].lower() == "check":
            params=params[1:]  
            if len(params) == 0:
                cacheStaticCheck()
                return True
            else:
                return False
        
        else:
            return False
    
    ### CONFIGURACIONES ###
    elif params[0] == "configuration":
        params=params[1:]
        
        ### LISTAR ###
        if params[0].lower() == "check":
            params=params[1:]    
            if len(params) == 0:
                configurationCheck()
                return True
            else:
                return False
            
        ### MODIFICAR ###
        elif params[0].lower() == "mod":
            params=params[1:]  
            if len(params) == 2:
                configurationModify(params[0], params[1])
                return True
            else:
                return False
        else:
            return False
        
    else:
        return False
    
    
servers = getServers()
if not servers:
    print("No hay nada configurado en servers.conf")
    sys.exit()

for server_name in servers:
    server = servers[server_name]
    try:
        db = dbman(server)
    except:
        print("Error intentando conectar el servidor: ",server_name)
        sys.exit()

if len(sys.argv) > 1:
    if not menu(sys.argv[1:]):
        showHelp()
else:
    showHelp()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    