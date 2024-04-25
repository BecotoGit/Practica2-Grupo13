
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
cur.execute("DROP TABLE IF EXISTS fechas_usuarios")
cur.execute("DROP TABLE IF EXISTS ips_usuarios")
cur.execute("DROP TABLE IF EXISTS emails")
cur.execute("DROP TABLE IF EXISTS legal")

cur.execute("CREATE TABLE IF NOT EXISTS usuarios("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "nombre TEXT,"
            "telefono INTEGER,"
            "contrasena TEXT,"
            "provincia TEXT,"
            "permisos TEXT"
            ");")

cur.execute("CREATE TABLE IF NOT EXISTS fechas_usuarios("
            "id INTEGER PRIMARY KEY,"
            "usuario_id INTEGER,"
            "fecha TEXT,"
            "FOREIGN KEY(usuario_id) REFERENCES usuarios(id)"
            ");")

cur.execute("CREATE TABLE IF NOT EXISTS ips_usuarios("
            "id INTEGER PRIMARY KEY,"
            "usuario_id INTEGER,"
            "ip TEXT,"
            "FOREIGN KEY (usuario_id) REFERENCES usuario(id)"
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
    usuario_data = elem[clave]

    cur.execute("INSERT OR IGNORE INTO usuarios(nombre, telefono, contrasena, provincia, permisos) VALUES (?, ?, ?, ?, ?)",
        (clave, usuario_data['telefono'], usuario_data['contrasena'], usuario_data['provincia'], usuario_data['permisos']))

    cur.execute("INSERT INTO emails (usuario, total, phishing, cliclados) VALUES (?, ?, ?, ?)",
        (clave, usuario_data['emails']['total'], usuario_data['emails']['phishing'], usuario_data['emails']['cliclados']))

    for fecha in usuario_data['fechas']:
        cur.execute("INSERT OR IGNORE  INTO fechas_usuarios (usuario_id, fecha) VALUES ((SELECT id FROM usuarios WHERE nombre = ?),?)", (clave, fecha))

    for ip in usuario_data['ips']:
        cur.execute("INSERT OR IGNORE INTO ips_usuarios (usuario_id, ip) VALUES ((SELECT id FROM usuarios WHERE nombre = ?),?)", (clave, ip))

con.commit()

for elem in dataLegal["legal"]:
    clave = list(elem.keys())[0]
    cur.execute("INSERT OR IGNORE INTO legal(web, cookies, aviso, proteccion_de_datos, creacion) VALUES(?,?,?, ?,?) ",
        (clave, elem[clave]['cookies'],elem[clave]['aviso'],elem[clave]['proteccion_de_datos'],elem[clave]['creacion']))

con.commit()
