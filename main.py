import sqlite3
import json


def readJson(name):
    path = "datos/" + name
    with open(path, "r") as file:
        data = json.load(file)
    return data

with open('datos/users_data_online.json','r') as fUsers:
    dataUsers = json.load(fUsers)

with open('datos/legal_data_online.json','r') as fLegal:
    dataLegal = json.load(fLegal)

con = sqlite3.connect('datos.db')
cur = con.cursor()

cur.execute("DROP TABLE IF EXISTS usuarios")
cur.execute("DROP TABLE IF EXISTS fechas_usuarios")
cur.execute("DROP TABLE IF EXISTS ips_usuarios")
cur.execute("DROP TABLE IF EXISTS emails")
cur.execute("DROP TABLE IF EXISTS legal")
cur.execute("DROP TABLE IF EXISTS conexiones_por_dia_usuario")

cur.execute("CREATE TABLE IF NOT EXISTS usuarios("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "nombre TEXT,"
            "telefono INTEGER,"
            "contrasena TEXT,"
            "provincia TEXT,"
            "permisos TEXT,"
            "critico INTEGER"
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
            "FOREIGN KEY (usuario_id) REFERENCES usuarios(id)"
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

cur.execute("CREATE TABLE IF NOT EXISTS conexiones_por_dia_usuario("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "fecha TEXT,"
            "num_conexiones INTEGER,"
            "num_usuarios INTEGER"
            ");")

con.commit()

for elem in dataUsers["usuarios"]:
    clave = list(elem.keys())[0]
    usuario_data = elem[clave]

    cur.execute("INSERT OR IGNORE INTO usuarios(nombre, telefono, contrasena, provincia, permisos, critico) VALUES (?, ?, ?, ?, ?, ?)",
        (clave, usuario_data['telefono'], usuario_data['contrasena'], usuario_data['provincia'], usuario_data['permisos'], usuario_data['critico']))

    cur.execute("INSERT INTO emails (usuario, total, phishing, cliclados) VALUES (?, ?, ?, ?)",
        (clave, usuario_data['emails']['total'], usuario_data['emails']['phishing'], usuario_data['emails']['cliclados']))

    for fecha in usuario_data['fechas']:
        cur.execute(
            "INSERT OR IGNORE INTO fechas_usuarios (usuario_id, fecha) VALUES ((SELECT id FROM usuarios WHERE nombre = ?), ?)",
            (clave, fecha))
    for ip in usuario_data['ips']:
        cur.execute("INSERT OR IGNORE INTO ips_usuarios (usuario_id, ip) VALUES ((SELECT id FROM usuarios WHERE nombre = ?),?)", (clave, ip))

con.commit()

cur.execute("""
    INSERT INTO conexiones_por_dia_usuario(fecha, num_conexiones, num_usuarios)
    SELECT fecha, COUNT(*) AS num_conexiones, COUNT(DISTINCT usuario_id) AS num_usuarios
    FROM fechas_usuarios
    GROUP BY fecha
""")
con.commit()
con.close()
