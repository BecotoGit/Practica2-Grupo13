import pandas as pd
import numpy as np
import sqlite3
import hashlib
import matplotlib.pyplot as plt

def isWeakPass(hashedPass, hashed_passwords):
    return hashedPass in hashed_passwords


def insertWeakPass(df):
    with open("SmallRockYou.txt", 'r', encoding='iso-8859-1') as f:
        SmallRockYou = {hashlib.md5(word.strip().encode()).hexdigest() for word in f}

    hashed_passwords = set(df['contrasena'])
    df['contrasenaDebil'] = df['contrasena'].apply(
        lambda x: 1 if isWeakPass(hashlib.md5(x.encode()).hexdigest(), SmallRockYou) else 0)
    return df

def obtener_datos():
    con = sqlite3.connect('datos.db')
    query = '''
        SELECT u.nombre, u.telefono, u.contrasena, u.provincia, 
               u.permisos, u.fechas, u.ips, 
               e.phishing AS emails_phishing
        FROM usuarios AS u
        LEFT JOIN emails AS e ON u.nombre = e.usuario
    '''
    df = pd.read_sql_query(query, con)
    con.close()
    return df

df = obtener_datos()
df = insertWeakPass(df)

# Agrupar por tipo de usuario (permisos) y calcular la media de fechas entre cambios de contraseña
media_tiempo_cambio = df.groupby('permisos')['fechas'].apply(lambda x: x.str.split(',').apply(len).mean())

# Graficar los resultados
plt.bar(media_tiempo_cambio.index, media_tiempo_cambio.values, color=['blue', 'orange'])
plt.xlabel('Tipo de Usuario')
plt.ylabel('Media de Tiempo entre Cambios de Contraseña')
plt.title('Comparación de Tiempo Promedio entre Cambios de Contraseña por Tipo de Usuario')
plt.xticks(rotation=45)
plt.show()