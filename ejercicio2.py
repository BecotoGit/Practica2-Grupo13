
import main
import pandas as pd
import numpy as np
import sqlite3


def obtener_datos():
    con = sqlite3.connect('datos.db')
    usuarios_df = pd.read_sql_query("SELECT * FROM usuarios", con)
    emails_df = pd.read_sql_query("SELECT * FROM emails", con)
    legal_df = pd.read_sql_query("SELECT * FROM legal", con)
    query_admin_phishing = """
            SELECT e.phishing
            FROM emails e
            INNER JOIN usuarios u ON e.usuario = u.nombre
            WHERE u.permisos = 1
        """
    admin_phishing_df = pd.read_sql_query(query_admin_phishing, con)
    con.close()
    return usuarios_df, emails_df, legal_df, admin_phishing_df


def num_muestras(df):
    #Numero de muestras (valores distintos de missing)
    df.replace('N,o,n,e', None, inplace=True)
    df.replace('None', np.nan, inplace=True)
    df_sin_none = df.dropna()
    muestras = len(df_sin_none)
    return muestras


def mean_std_fechas(df):
    #Media y desviación estándar del total de fechas en las que se ha cambiado la contraseña
    df['fechas'] = df['fechas'].str.split(',')
    df['cambios'] = df['fechas'].apply(len)
    media = df['cambios'].mean()
    desviacion = df['cambios'].std()
    return media, desviacion


def mean_std_ips(df):
    # Media y desviación estándar del total de IPs que se han detectado
    df['ips'] = df['ips'].replace('N,o,n,e', None)
    df['ips'] = df['ips'].str.split(',')
    df['num_ips'] = df['ips'].apply(lambda x: len(x) if x is not None else None)
    media = df['num_ips'].mean()
    desviacion = df['num_ips'].std()
    return media, desviacion


def mean_std_phishing(df):
    # Media y desviación estándar del número de email recibidos de phishing en los que ha interactuado cualquier usuario
    media_phishing = df['phishing'].mean()
    desviacion_phishing = df['phishing'].std()
    return media_phishing, desviacion_phishing


def min_max_emails(df):
    # Valor mínimo y máximo del total de emails recibidos
    min_emails = df['total'].min()
    max_emails = df['total'].max()
    return min_emails, max_emails


def min_max_phishing_admin(df_admin):
    # Valor mínimo y máximo del número de emails de phishing en los que ha interactuado un administrador
    min_phishing_admin = df_admin['phishing'].min()
    max_phishing_admin = df_admin['phishing'].max()
    return min_phishing_admin, max_phishing_admin

def printInfo():
    usuarios_df, emails_df, legal_df, admin_phishing_df = obtener_datos()
    n_muestras = num_muestras(usuarios_df)
    print("Numero de muestras (valores distintos de missing): ", n_muestras)
    media_fechas, desviacion_fechas = mean_std_fechas(usuarios_df)
    print("Media del total de fechas en las que se ha cambiado la contraseña: ", media_fechas)
    print("Desviación estándar del total de fechas en las que se ha cambiado la contraseña: ", desviacion_fechas)

    media_ips, desviacion_ips = mean_std_ips(usuarios_df)
    print("Media estándar del total de IPs que se han detectado: ", media_ips)
    print("Desviación estándar del total de IPs que se han detectado: ", desviacion_ips)

    media_phishing, desviacion_phishing = mean_std_phishing(emails_df)
    print("Media total del número de email recibidos de phishing en los que ha interactuado cualquier usuario: ", media_phishing)
    print("Desviación estándar del número de email recibidos de phishing en los que ha interactuado cualquier usuario: ", desviacion_phishing)

    min_emails, max_emails = min_max_emails(emails_df)
    print("Valor máximo del total de emails recibidos: ", max_emails)
    print("Valor mínimo del total de emails recibidos: ", min_emails)

    min_phishing_admin, max_phishing_admin = min_max_phishing_admin(admin_phishing_df)
    print("Valor mínimo del número de emails de phishing en los que ha interactuado un administrador: ", min_phishing_admin)
    print("Valor máximo del número de emails de phishing en los que ha interactuado un administrador: ", max_phishing_admin)

#printInfo()