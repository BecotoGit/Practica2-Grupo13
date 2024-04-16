
import sqlite3
import pandas as pd
import json


def readJson(name):
    # Devuelve el diccionario con los datos
    path = "datos/" + name
    file = open(path, "r")
    data = json.load(file)
    file.close()
    return data


fUsers = open('datos/users_data_online.json','r')
fLegal = open('datos/legal_data_online.json','r')

dataUsers = json.load(fUsers)            #readJson('user_data_online.json')
dataLegal = json.load(fLegal)            #readJson('legal')

fUsers.close()
fLegal.close()

con = sqlite3.connect('datos.db')
cur = con.cursor()
cur.execute("DROP TABLE IF EXISTS usuarios")
cur.execute("DROP TABLE IF EXISTS emails")
cur.execute("DROP TABLE IF EXISTS legal")

cur.execute("CREATE TABLE IF NOT EXISTS usuarios("
            "nombre TEXT PRIMARY KEY,"
            "telefono INTEGER,"
            "contrasena TEXT,"
            "provincia TEXT,"
            "permisos TEXT,"
            "fechas TEXT,"
            "ips TEXT"
            ");")


cur.execute("CREATE TABLE IF NOT EXISTS emails("
            "usuario TEXT PRIMARY KEY,"
            "total INTEGER,"
            "phishing INTEGER,"
            "cliclados INTEGER,"
            "FOREIGN KEY (usuario) REFERENCES usuarios(nombre) "
            ");")

cur.execute("CREATE TABLE IF NOT EXISTS legal("
            "web TEXT PRIMARY KEY,"
            "cookies INTEGER,"
            "aviso INTEGER,"
            "proteccion_de_datos INTEGER,"
            "creacion INTEGER"
            ");")

con.commit()

for elem in dataUsers["usuarios"]:
    clave = list(elem.keys())[0]
    cur.execute("INSERT OR IGNORE INTO usuarios(nombre, telefono, contrasena, provincia, permisos, fechas, ips) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (clave, elem[clave]['telefono'], elem[clave]['contrasena'], elem[clave]['provincia'], elem[clave]['permisos'],
            ','.join(elem[clave]['fechas']), ','.join(elem[clave]['ips'])))

    cur.execute("INSERT INTO emails (usuario, total, phishing, cliclados) VALUES (?, ?, ?, ?)",
        (clave, elem[clave]['emails']['total'], elem[clave]['emails']['phishing'], elem[clave]['emails']['cliclados']))

con.commit()

for elem in dataLegal["legal"]:
    clave = list(elem.keys())[0]
    cur.execute("INSERT OR IGNORE INTO legal(web, cookies, aviso, proteccion_de_datos, creacion) VALUES(?,?,?, ?,?) ",
        (clave, elem[clave]['cookies'],elem[clave]['aviso'],elem[clave]['proteccion_de_datos'],elem[clave]['creacion']))

con.commit()
