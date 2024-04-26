import sqlite3
import requests
from flask import Flask, render_template, request

import ejercicio2
from ejercicio3 import prepareDf

app = Flask(__name__)
def connect_db():
    return sqlite3.connect('datos.db')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/graph')
def graph():
    return render_template('grafico.html')

@app.route('/model')
def model():
    return render_template('model.html')

@app.route('/topUsers')
def users():
    return

@app.route('/topWebs')
def web():
    return
@app.route('/ej2')
def ej2():
    usuarios_df, emails_df, legal_df, admin_phishing_df = ejercicio2.obtener_datos()

    n_muestras = ejercicio2.num_muestras(usuarios_df)
    media_fechas, desviacion_fechas = ejercicio2.mean_std_fechas(usuarios_df)
    media_ips, desviacion_ips = ejercicio2.mean_std_ips(usuarios_df)
    media, desviacion_estandar = ejercicio2.mean_std_phishing(emails_df)
    minimo, maximo = ejercicio2.min_max_emails(emails_df)
    minimo_admin, maximo_admin = ejercicio2.min_max_phishing_admin(admin_phishing_df)
    return render_template('ej2.html', num_muestras=n_muestras, media_fechas=media_fechas,
                           desviacion_fechas=desviacion_fechas, media_ips=media_ips, desviacion_ips=desviacion_ips,
                           media=media, desviacion_estandar=desviacion_estandar, minimo=minimo, maximo=maximo,
                           minimo_admin=minimo_admin, maximo_admin=maximo_admin)

@app.route('/ej3')
def ej3():
    df = prepareDf()

    data = {"grupo": list(), "num_muestras": list(), "missing": list(), "median": list(), "mean": list(),
            "var": list(), "min": list(), "max": list()}
    for grupo, data_group in df.groupby(['permisos', 'contrasenaDebil']):
        data['grupo'].append(grupo)
        data['num_muestras'].append(len(data_group['phishing']))
        data['missing'].append((data_group['phishing'] == 0).sum())
        data['median'].append(data_group['phishing'].median())
        data['mean'].append(data_group['phishing'].mean())
        data['var'].append(data_group['phishing'].var())
        data['min'].append(data_group['phishing'].min())
        data['max'].append(data_group['phishing'].max())

    return render_template('prueba.html', data=data)


@app.route('/top_usuarios_criticos')
def top_usuarios_criticos():
    x = request.args.get('x', default=5, type=int)  # Obtener el valor de X de la consulta, valor predeterminado: 10
    spam_percentage = request.args.get('spam_percentage', default='any')  # Obtener el valor de spam_percentage
    con = connect_db()
    cur = con.cursor()

    # Si se especifica el porcentaje de spam, ajustar la consulta
    if spam_percentage == 'more_than_50':
        cur.execute("""
                   SELECT u.nombre, u.telefono, u.provincia
                   FROM usuarios u
                   JOIN (
                       SELECT usuario, 
                              phishing AS total_phishing,
                              cliclados AS total_cliclados
                       FROM emails
                       GROUP BY usuario
                   ) e ON u.nombre = e.usuario
                   WHERE critico = 1
                   AND (CAST(e.total_cliclados AS REAL) / e.total_phishing) > 0.5
                   ORDER BY u.nombre ASC LIMIT ?
                   """, (x,))
    elif spam_percentage == 'less_than_50':
        cur.execute("""SELECT u.nombre, u.telefono, u.provincia
                   FROM usuarios u
                   JOIN (
                       SELECT usuario,
                              phishing AS total_phishing,
                              cliclados AS total_cliclados
                       FROM emails
                       GROUP BY usuario
                   ) e ON u.nombre = e.usuario
                   WHERE critico = 1
                   AND (CAST(e.total_cliclados AS REAL) / e.total_phishing) <= 0.5
                   ORDER BY u.nombre ASC LIMIT ?""", (x,))
    else:
        cur.execute("""
                SELECT nombre, telefono, provincia
                FROM usuarios 
                WHERE critico = 1
                ORDER BY nombre ASC LIMIT ?
                """, (x,))
    usuarios_criticos = cur.fetchall()
    con.close()
    return render_template('usuarios_criticos.html', usuarios_criticos=usuarios_criticos)
@app.route('/top_paginas_desactualizadas')
def top_paginas_desactualizadas():
    x = request.args.get('xWeb', default=5, type=int)
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT web FROM legal WHERE cookies > 0 OR aviso > 0 OR proteccion_de_datos > 0 ORDER BY (cookies + aviso + proteccion_de_datos), creacion LIMIT ?", (x,))
    paginas_desactualizadas = cur.fetchall()
    con.close()
    return render_template('paginas_desactualizadas.html', paginas_desactualizadas=paginas_desactualizadas)


@app.route('/ultimas_vulns')
def ultimas_vulns():
    response = requests.get('https://cve.circl.lu/api/last/10')
    if response.status_code == 200:
        cves = response.json()
        return render_template('ultimas_vulns.html', cves=cves)
    else:
        return 'Error al obtener los datos de CVE'

if __name__ == '__main__':
    app.run(debug = True)
