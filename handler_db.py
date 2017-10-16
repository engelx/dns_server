# -*- coding: utf-8 -*-
"""
@title           :MiniServerDNS
@author          :Engelx (Miguel A. Diaz)
@email           :mgldzm@gmail.com 
@date            :2017-08-31
@version         :0.7
@python_version  :3.5
"""

from handler_db_pg import dbman_pg as db_base
import time, json
from sys import exit

class dbman:
    
    # Se llama a la clase solo con el array servidor 
    def __init__(self, server):
        self.db = db_base(server["host"],server["port"],server["user"],server["pass"],server["dbname"]) #conexión
        self.conf = self.getConfig() # Se extrae la configuración
    
    # Convertirdor de str a tipos según contenido
    def _convty(self, element): 
        if not type(element) is str:
            return element
        elif element.lower() == 'true' or element.lower() == 'false':
            return bool(element.lower() == "true")
        elif element.isdigit():
            return int(element)
        else:
            return element
    
    # Obtiene la tabla configuración y la convierte en array
    def getConfig(self, element=False): 
        value = None
        if element:
            value = self._convty(self.db.select("configuration", "name='{}'".format(element))[0][1])
        else:
            value = self.db.select("configuration")
            temp = {}
            for i in value:
                temp[i[0]]= self._convty(i[1])
                
            value = temp
        return value
    
    # Revisa el si host está bloqueado para una ip especifica
    def blocked(self, host, ip): 
        value = self.db.select("blacklist as b, exceptions as e, users as u ", "u.ip = '{}' and '.{}' like b.host and u.ip=e.ip and b.host not like e.host".format(ip,host))
        if value:
            return True
        return False

    # Revisa si el host está en caché, si se pasa ip, la carga
    def cache(self, host, ip=None): 
        
        # Si ip, carga nueva ip
        if ip: 
            self.db.delete("cache", "host='{}'".format(host))
            self.db.insert("cache","host,ip,expire,fixed","'{}', '{}', {}, 'False'".format(host, ip, int(time.time())))
            self.db.commit()
            return ip
        
        #limpiamos la DB de las resoluciones vencidas
        self.db.delete("cache", "expire<{} and fixed='False'".format(int(time.time()-self.conf["cache_expiration"])))
        self.db.commit()
        
        # Revisa si el host está en la DB
        value = self.db.select("cache", "host='{}'".format(host),"ip")
        if not value:
            return False
        
        # Si está returnamos la ip
        return value[0][0]

    # Genera el log de actualizaciones
    def log(self, host, ip, answer): 
        fields = "id, ip, date, host, answer"
        date = time.strftime("%Y-%m-%d %H:%M:%S")
        values = "(select count(id)+1 from logs), '{}', '{}', '{}', '{}'".format(ip,date,host,answer)
        self.db.insert("logs",fields, values)
        self.db.commit()
    
    
    ###########################################################################
    ##### FIN FUNCIONES DEL SERVIDOR
    ##### INICIO FUNCIONES DEL CONFIGURADOR
    ###########################################################################
    
    # TEST
    def cleanDB(self):
        self.db.delete("users","true")
        self.db.delete("blacklist","true")
        self.db.delete("exceptions","true")
        self.db.commit()
    
    
    # Agregar usuario
    def userAdd(self, name, group, ip): 
        fields = '"name", "group", ip'
        values = "'{}', '{}', '{}'".format(name.upper(), group.upper(), ip)
        self.db.insert("users",fields, values)
        return self.db.commit()

    # Remover usuario
    def userRem(self, name, group=False):
        # Si el nombre pasado pertenece a un grupo
        if group: 
            group = 'group'
        else:
            group = 'name'
        
        # Removemos las excepciones relacionadas al usuario        
        sql = "DELETE FROM exceptions WHERE ip IN (SELECT ip FROM users WHERE users.{} ILIKE '{}')"
        self.db.execute(sql.format(group, name.upper()))
        
        # Removemos al usuario
        self.db.delete("users", "users.{} ILIKE '{}'".format(group, name.upper()))
        
        return self.db.commit()
    
    # Listar Usuarios
    def userCheck(self, group=False):
        if not group: group = "%"
        users = self.db.select("users", "users.group ILIKE '{}' ORDER BY users.group".format(group), "ip, users.name, users.group")
        return users
    
    # Añadir excepcion
    def exceptionAdd(self, name, host=False, group=False):
        if not host: 
            host = '%'
        else:
            host = "%." + host.lower()
        
        # Si el nombre pasado pertenece a un grupo
        if group:
            group = 'group'
        else:
            group = 'name'

        if host == "%":
            sql = "DELETE FROM exceptions WHERE ip IN (SELECT ip FROM users WHERE users.{} ILIKE '{}')"
            self.db.execute(sql.format(group, name.upper()))
            
        # Insertamos as excepciones en base a la ip relacionadas al usuario
        
        sql = "INSERT INTO exceptions (host, ip) "
        sql += "SELECT '{}', ip FROM users where not ip in ("
        sql += "select ip from exceptions where host = '%' or host = '{}'"
        sql += ") and users.{} = '{}'"
        self.db.execute(sql.format(host.lower(), host.lower(), group, name.upper()))
        return self.db.commit()
        
    # Remover excepción
    def exceptionRem(self, user, host=False, group=False):
        # Si no hay host, indica todos
        if not host: 
            host = "%"
        else:
            host = "%."+host
            
        if group:
            group = 'group'
        else:
            group = 'name'
            
        # Removemos las excepciones relacionadas al usuario
        sql = "DELETE FROM exceptions WHERE ip IN (SELECT ip FROM users WHERE users.{} ILIKE '{}') AND host = '{}'".format(group, user.upper(), host.lower())
        self.db.execute(sql)
        return self.db.commit()
    
    # Lista excepciones
    def exceptionCheck(self, user=False, group=False):
        if not user: 
            user = "%"
        if group:
            group = 'group'
        else:
            group = 'name'
        
        # Obtenemos las excepciones con nombre de usuario
        return self.db.select("exceptions AS e, users AS u", "u.ip=e.ip AND u.{} ILIKE '{}'".format(group, user.lower()), "u.name, u.ip, REPLACE(REPLACE(e.host, '%.', ''), '%', 'LIBRE')")
            
    # Añadir hosts Bloqueados   
    def blockAdd(self, host, cat):
        # Aseguramos que capture subdominios
        host = "%." + host 
        fields = "host, category"
        values = "'{}', '{}'".format(host.lower(), cat.upper())
        self.db.insert("blacklist", fields, values)
        return self.db.commit()
    
    # Eliminar hosts bloqueados
    def blockRem(self, host, cat=False):   
        if cat:
            self.db.delete("blacklist", "category='{}'".format(host.upper()))
        else:
            self.db.delete("blacklist", "host='%.{}'".format(host.lower()))
        return self.db.commit()
    
    def blockCheck(self, cat=False):
        if cat:
            return self.db.select("blacklist", "category='{}'".format(cat), "host, category")
        else:
            return self.db.select("blacklist", "true", "host, category")
        
    # Agrega un host fijo al Cache
    def cacheStaticAdd(self, host, ip):
        fields = "host, ip, expire, fixed"
        values = "'{}', '{}', 0, 'True'".format(host.lower(), ip)
        self.db.insert("cache", fields, values)
        return self.db.commit()
        
    # Remueve un host fijo del Cache
    def cacheStaticRem(self, host):
        self.db.delete("cache", "host ILIKE '{}' and fixed='True'".format(host.lower()))
        return self.db.commit()
    
    # Lista los hosts fijos en Cache
    def cacheStaticCheck(self):
        return self.db.select("cache", "fixed='True'", "host, ip")
    
    def configurationModify(self, field, value):
        self.db.update("configuration", "value='{}'".format(value), "name='{}'".format(field))
        return self.db.commit()
    
    
    # Muestra la configuración del servidor
    def configurationCheck(self):
        return self.db.select("configuration", "true", "name, value")
        
    def close(self):
        self.db.close()