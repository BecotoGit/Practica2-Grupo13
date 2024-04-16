
import pandas as pd
import numpy as np
import sqlite3
import hashlib


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
               e.phishing AS phishing
        FROM usuarios AS u
        LEFT JOIN emails AS e ON u.nombre = e.usuario
    '''
    df = pd.read_sql_query(query, con)
    con.close()
    return df


df = obtener_datos()

df = insertWeakPass(df)

con = sqlite3.connect('datos.db')
df.to_sql('usuarios_debil', con, if_exists='replace', index=False)

df = pd.read_sql_query('SELECT * FROM usuarios_debil', con)

for group, data_group in df.groupby(['permisos', 'contrasenaDebil']):
    print(f"Grupo: {group}")
    print(f"Número de observaciones: {len(data_group)}")
    num_missing = (data_group['phishing'] == 0).sum()
    print(f"Número de valores ausentes (missing): {num_missing}")
    print(f"Mediana: {data_group['phishing'].median()}")
    print(f"Media: {data_group['phishing'].mean()}")
    print(f"Varianza: {data_group['phishing'].var()}")
    print(f"Valor máximo: {data_group['phishing'].max()}")
    print(f"Valor mínimo: {data_group['phishing'].min()}")
