import sqlite3
import threading

import aiohttp
import numpy as np
import pandas as pd
import requests
from flask import Flask, json, render_template, request, make_response, send_file
import asyncio
from flask import Flask, render_template, request, make_response, send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from joblib import load
from joblib import dump
from sklearn.calibration import LabelEncoder
from Modelos import Linear_Regresion, Regresion_Predict, Arbol_Decision, Arbol_Decision_Predict, forest, Forest_Predict


app = Flask(__name__)
data_vulns = None

def connect_db():
    return sqlite3.connect('datos.db')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/top_usuarios_criticos')
def top_usuarios_criticos():
    x = request.args.get('x', default=5, type=int)
    spam_percentage = request.args.get('spam_percentage', default='any')
    con = connect_db()
    cur = con.cursor()

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


@app.route('/top_usuarios_criticos_pdf')
def top_usuarios_criticos_pdf():
    x = request.args.get('x', default=5, type=int)  #
    spam_percentage = request.args.get('spam_percentage', default='any')
    con = connect_db()
    cur = con.cursor()

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
    pdf_data = generate_pdf(usuarios_criticos)
    return send_pdf(pdf_data, 'usuarios_criticos.pdf')


@app.route('/top_paginas_desactualizadas_pdf')
@app.route('/top_paginas_desactualizadas')
def top_paginas_desactualizadas():
    x = request.args.get('xWeb', default=5, type=int)
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT web FROM legal WHERE cookies > 0 OR aviso > 0 OR proteccion_de_datos > 0 ORDER BY (cookies + aviso + proteccion_de_datos), creacion LIMIT ?", (x,))
    paginas_desactualizadas = cur.fetchall()
    con.close()
    return render_template('paginas_desactualizadas.html', paginas_desactualizadas=paginas_desactualizadas)


def top_paginas_desactualizadas_pdf():
    x = request.args.get('xWeb', default=5, type=int)
    con = connect_db()
    cur = con.cursor()
    cur.execute(
        "SELECT web FROM legal WHERE cookies > 0 OR aviso > 0 OR proteccion_de_datos > 0 ORDER BY (cookies + aviso + proteccion_de_datos), creacion LIMIT ?",
        (x,))
    paginas_desactualizadas = cur.fetchall()
    con.close()
    pdf_data = generate_paginas_pdf(paginas_desactualizadas)
    return send_pdf(pdf_data, 'paginas_desactualizadas.pdf')


def generate_pdf(data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']

    content = []
    content.append(Paragraph("Usuarios Críticos", styles['Title']))
    content.append(Paragraph("<br/><br/>", style_normal))

    table_data = [["Nombre", "Teléfono", "Provincia"]]
    for usuario in data:
        table_data.append([usuario[0], usuario[1], usuario[2]])
    t = Table(table_data)
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                           ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                           ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                           ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                           ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                           ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                           ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    content.append(t)

    doc.build(content)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data


def generate_paginas_pdf(data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']

    content = []
    content.append(Paragraph("Páginas Desactualizadas", styles['Title']))
    content.append(Paragraph("<br/><br/>", style_normal))

    for pagina in data:
        content.append(Paragraph(pagina[0], style_normal))


    doc.build(content)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data


def send_pdf(pdf_data, filename):
    response = make_response(pdf_data)
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    response.headers['Content-Type'] = 'application/pdf'
    return response


@app.route('/ultimas_vulns')
def ultimas_vulns():
    response = requests.get('https://cve.circl.lu/api/last/10')
    if response.status_code == 200:
        cves = response.json()
        return render_template('ultimas_vulns.html', cves=cves)
    else:
        return 'Error al obtener los datos de CVE'


@app.route('/ultimas_vulns_pdf')
def ultimas_vulns_pdf():
    response = requests.get('https://cve.circl.lu/api/last/10')
    if response.status_code == 200:
        cves = response.json()
        pdf_data = generate_cves_pdf(cves)
        return send_pdf(pdf_data, 'ultimas_vulns.pdf')
    else:
        return 'Error al obtener los datos de CVE'


def generate_cves_pdf(cves):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("Últimas Vulnerabilidades CVE", styles['Title']))
    for cve in cves:
        content.append(Paragraph(f"{cve['id']}: {cve['summary']}", styles['Normal']))

    doc.build(content)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data


@app.route('/conexiones_usuario')
def conexiones_usuario():
    con = connect_db()
    cur = con.cursor()
    cur.execute("""
        SELECT fecha, COUNT(*) AS num_conexiones, GROUP_CONCAT(usuario_id) AS ids_usuarios
        FROM fechas_usuarios
        GROUP BY fecha
        ORDER BY fecha
    """)
    conexiones_usuario = cur.fetchall()
    con.close()
    return render_template('conexiones_usuario.html', conexiones_usuario=conexiones_usuario)

def generate_conexiones_usuario_pdf(data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']

    content = []
    content.append(Paragraph("Conexiones de Usuarios por Día", styles['Title']))
    content.append(Paragraph("<br/><br/>", style_normal))

    table_data = [["Fecha", "Número de Conexiones", "IDs de Usuarios"]]
    for conexion in data:
        table_data.append([conexion[0], conexion[1], conexion[2]])

    t = Table(table_data)
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                           ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                           ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                           ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                           ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                           ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                           ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    content.append(t)

    doc.build(content)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data

from flask import send_file

@app.route('/conexiones_usuario_pdf')
def conexiones_usuario_pdf():
    con = connect_db()
    cur = con.cursor()
    cur.execute("""
        SELECT fecha, COUNT(*) AS num_conexiones, GROUP_CONCAT(usuario_id) AS ids_usuarios
        FROM fechas_usuarios
        GROUP BY fecha
        ORDER BY fecha
    """)
    conexiones_usuario = cur.fetchall()
    con.close()
    pdf_data = generate_conexiones_usuario_pdf(conexiones_usuario)
    return send_pdf(pdf_data, 'conexiones_usuario.pdf')

@app.route('/analizar_usuario', methods=['GET', 'POST'])
def predict():
    if request.method == 'GET':
        return render_template('formulario_ejercicio5.html')
    else:
        # Conectar con la base de datos SQLite
        conn = sqlite3.connect('datos.db')

        # Leer los datos relevantes de la base de datos
        df = pd.read_sql_query('''
            SELECT u.nombre, u.telefono, u.provincia, u.permisos, e.total, e.phishing, e.cliclados
            FROM usuarios u
            INNER JOIN emails e ON u.nombre = e.usuario
            ''', conn)

        for indice_fila, fila in df.iterrows():
            for columna in df.columns:
                # Verificar si el valor en la celda es 'None'
                if fila[columna] == 'None':
                    # Cambiar 'None' a None
                    df.at[indice_fila, columna] = None

        df_sin_none = df.dropna()

        # Copia del dataframe sin valores nulos
        df_sin_none_copy = df_sin_none.copy()

        # Inicializar el codificador de etiquetas
        label_encoder = LabelEncoder()

        # Ajustar y transformar la columna 'provincia' usando el codificador de etiquetas
        df_sin_none_copy['provincia'] = label_encoder.fit_transform(df_sin_none_copy['provincia'])

        # Mapeo de las etiquetas a las categorías originales
        mappings = {index: label for index, label in enumerate(label_encoder.classes_)}

        # Cargar el archivo users_data_online_clasificado.json
        with open('users_data_online_clasificado.json') as f:
            data_json = json.load(f)

        # Convertir el JSON en un DataFrame
        df_json = pd.DataFrame(data_json)

        # Lista para almacenar los valores de 'criticos'
        criticos_lista = []
        for fila_json in df_json['usuarios']:
            for nombre_usuario, datos_usuario in fila_json.items():
                if nombre_usuario in df_sin_none['nombre'].values:
                    critico = datos_usuario.get('critico', None)
                    criticos_lista.append(critico)

        # Separar las características (X) y las etiquetas (y)
        X = df_sin_none_copy.drop(columns=['nombre'])  # Características: todas las columnas excepto 'nombre'
        y = criticos_lista  # Etiquetas: columna 'critico'

        regr_model = Linear_Regresion(X, y)  
        tree_model = Arbol_Decision(X, y)  
        forest_model = forest(X, y) 

        modelo = request.form['method']
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        provincia = request.form['provincia']
        permisos = int(request.form['permisos'])
        total = int(request.form['total'])
        phishing = int(request.form['phishing'])
        cliclados = int(request.form['cliclados'])

        if nombre not in df_sin_none['nombre'].values:
            return render_template('error.html', mensaje='Usuario no encontrado en la base de datos')

        es_critico = None

        if modelo == 'Regresión Lineal':
            resultado = Regresion_Predict(regr_model, nombre, telefono, provincia, permisos, total, phishing, cliclados)
            es_critico = resultado
        elif modelo == 'Árbol de Decisión':
            resultado = Arbol_Decision_Predict(tree_model, nombre, telefono, provincia, permisos, total, phishing, cliclados)
            es_critico = resultado == 1
        elif modelo == 'Bosque Aleatorio':
            resultado = Forest_Predict(forest_model, nombre, telefono, provincia, permisos, total, phishing, cliclados)
            es_critico = resultado == 1

        return render_template('resultado_prediccion.html', es_critico=es_critico)


if __name__ == '__main__':
    app.run(debug = True)

