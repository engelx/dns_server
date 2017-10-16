# -*- coding: utf-8 -*-
"""
@title           :MiniServerDNS
@author          :Engelx (Miguel A. Diaz)
@email           :mgldzm@gmail.com 
@date            :2017-08-31
@version         :0.7
@python_version  :3.5
"""

def byteToInt(byteArray):
    return [int(x) for x in byteArray]
def IntToByte(intArray):
    return bytearray(intArray)

def processQuery(data):
    data = byteToInt(data)
    if (data[2] & 252) != 0: # not standard query
        return data, False
    
    if data[4] != 0 and data[5] > 1: # no accept more than single query... maybe in future
        return data, False

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
    
    pointer += 1
    
    if data[12+pointer] == 0 and (data[12+pointer+1] == 1 or data[12+pointer+1] == 28): # if A or AAAA
        if data[12+pointer+1] == 28:
            data[12+pointer+1] = 1 # override AAAA as A
    else: # if not
        return data, False
    
    pointer += 2
    
    if data[12+pointer] != 0 or data[12+pointer+1] != 1: # if not IN
        return data, False
    
    return data, host

def generateResponse(data, ip=False):
    data[2] |= 1<<7 # change query to response
    data[3] |= 1<<7 # recursive
    data[7] = 1 # 1 answer
    
    if not ip: # if domain not found
        data[3] |= 3
    
    if not ip:
        return IntToByte(data)
    
    data.extend([0xc0, 0x0c]) # answer indicator
    data.extend([0x00, 0x01]) # 2 byte for type
    data.extend([0x00, 0x01]) # 2 byte for class
    data.extend([0x00, 0x00, 0x02, 0x00]) # 4 byte for TTL, 600 sec
    data.extend([0x00, 0x04]) # 2 byte length of ip
    data.extend([int(x) for x in ip.split(".")]) #ip
    return IntToByte(data)
    
def processResponse(data):
    data = byteToInt(data)
    if data[3] & 3:
        return False
    return ".".join([str(x) for x in data[-4:]])