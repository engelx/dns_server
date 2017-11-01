# -*- coding: utf-8 -*-
"""
@title           :MiniServerDNS
@author          :Engelx (Miguel A. Diaz)
@email           :mgldzm@gmail.com 
@date            :2017-08-31
@version         :0.7
@python_version  :3.5
"""
import socket

class dnsListener():
    def __init__(self):
        self.con = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # open listen socket
        self.con.bind(('',53)) # as port 53, DNS
        
    def waitQuery(self, timeout): 
        self.con.settimeout(timeout)
        try:
            data, con = self.con.recvfrom(512) #read packet
            if not data : 
                return False
            self.client = type('x', (object,), {"pair":con, "ip":con[0], "port":con[1]})
            self.request = type('x', (object,), {"data":data, "con":con})
            return True
        except socket.timeout:
            return False
    
    def send(self, addr, data):
        self.con.sendto(data, addr)


    def forwardToDns(self, ip, data, timeout):
        con = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # open listen socket
        con.settimeout(timeout)
        con.connect((ip, 53))
        con.send(data)
        
        try: #si hubo respuesta
            return con.recv(2048)
        except socket.timeout: #si no hubi respuesta
            return False
    

class dnsQuery():
    
    def __init__(self, request):
        self.con = request.con
        self.inData = request.data
        self.processQuery()
        
    
    def byteToInt(self, byteArray):
        return [int(x) for x in byteArray]
    
    def IntToByte(self, intArray):
        return bytearray(intArray)
    
    def processQuery(self):
        data = self.byteToInt(self.inData)
        if (data[2] & 252) != 0: # not standard query
            self.data = self.IntToByte(data)
            return False
        
        if data[4] != 0 and data[5] > 1: # no accept more than single query... maybe in future
            self.data = self.IntToByte(data)
            return False
    
        host = ""
        section = data[12] # length first piece
        pointer = 1
        while section > 0:
            host += chr(data[12+pointer])
            section -= 1
            pointer += 1
            if section == 0:
                section = data[12+pointer]
                if section != 0:
                    host += "."
                else:
                    break
                pointer += 1
        
        self.host = host
        
        pointer += 1
        
        if data[12+pointer] == 0 and (data[12+pointer+1] == 1 or data[12+pointer+1] == 28): # if A or AAAA
            if data[12+pointer+1] == 28:
                data[12+pointer+1] = 1 # override AAAA as A
        else: # if not
            self.data = self.IntToByte(data)
            return False
        
        pointer += 2
        
        if data[12+pointer] != 0 or data[12+pointer+1] != 1: # if not IN
            self.host = False
        
        self.data = self.IntToByte(data)
        return True
    
    def response(self, ip=False):
        data = self.byteToInt(self.data)
        data[2] |= 1<<7 # change query to response
        data[3] |= 1<<7 # recursive
        data[7] = 1 # 1 answer
        
        if not ip: # if domain not found
            data[3] |= 3
        
        if ip:
            data.extend([0xc0, 0x0c]) # answer indicator
            data.extend([0x00, 0x01]) # 2 byte for type
            data.extend([0x00, 0x01]) # 2 byte for class
            data.extend([0x00, 0x00, 0x02, 0x00]) # 4 byte for TTL, 600 sec
            data.extend([0x00, 0x04]) # 2 byte length of ip
            data.extend([int(x) for x in ip.split(".")]) #ip
        self.data = self.IntToByte(data)
        return self.data
        
    def processResponse(self, data):
        data = self.byteToInt(data)
        if data[3] & 3:
            return False
        return ".".join([str(x) for x in data[-4:]])