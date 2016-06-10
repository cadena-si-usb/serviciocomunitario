# -*- coding: utf-8 -*-
import ldap 
import string
import random

# Requiere:
# sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev ldap-utils
# pip install ldap

def get_ldap_data(usbid):
    def getFirst(maybeList):
        # Evitar excepcion de index no encontrado
        if type(maybeList)==list and len(maybeList)>0:
            return maybeList[0]
        else:
            return None

    user = {}
    l    = ldap.open("ldap.usb.ve")
    searchScope        = ldap.SCOPE_SUBTREE
    retrieveAttributes = None #Traemos todos los atributos
    baseDN = "ou=People,dc=usb,dc=ve"
    searchFilter = "uid=*"+usbid+"*"
    ldap_result_id = l.search(baseDN,searchScope,searchFilter,retrieveAttributes)
    result_type, consulta = l.result(ldap_result_id, 0)
    datos = consulta[0][1]

    #print datos

    # Extraer datos evitando campos inexistentes
    user['first_name'] = getFirst(datos.get('givenName'))
    user['last_name']  = getFirst(datos.get('sn'))
    user['email']      = getFirst(datos.get('mail'))
    user['cedula']     = getFirst(datos.get('personalId'))
    user['phone']      = getFirst(datos.get('mobile'))
    user_type          = getFirst(datos.get('gidNumber'))

    if user_type == "1000":
        user['tipo'] = "Docente"
        user['dpto'] = getFirst(datos.get('department'))
    elif user_type == "1002":
        user['tipo'] = "Empleado"
    elif user_type == "1003":
        user['tipo'] = "Organización"
    elif user_type == "1004":
        user['tipo'] = "Pregrado"
        user['carrera'] = getFirst(datos.get('career'))
    elif user_type == "1006":
        user['tipo'] = "Postgrado"
        user['carrera'] = getFirst(datos.get('career'))
    elif user_type == "1007":
        user['tipo'] = "Egresado"
    elif user_type == "1008":
        user['tipo'] = "Administrativo"

    return user

def random_key():
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(20))
