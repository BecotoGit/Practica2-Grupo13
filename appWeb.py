import sqlite3

import numpy as np
import requests
from flask import Flask, render_template, request, make_response, send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from joblib import load
from joblib import dump


app = Flask(__name__)


def connect_db():
    return sqlite3.connect('datos.db')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analizar_usuario', methods=['GET', 'POST'])
def analizar_usuario():
    nombre = request.form['nombre']
    telefono = request.form['telefono']
    provincia = request.form['provincia']
    permisos = request.form['permisos']
    total = request.form['total']
    phishing = request.form['phishing']
    cliclados = request.form['cliclados']
    method = request.form['method']

    total = float(total)
    phishing = float(phishing)
    cliclados = float(cliclados)

    porcentaje_phishing_cliclados = (phishing / cliclados) * 100
    critico = 1 if porcentaje_phishing_cliclados > 50 else 0
    usuario = {'nombre': nombre, 'telefono': telefono, 'provincia': provincia, 'permisos': permisos, 'total': total,
               'phishing': phishing, 'cliclados': cliclados, 'critico': critico}


    prediction = predict_user_criticity(nombre, total, phishing, cliclados, method)

    return render_template('resultado_analisis.html', usuario=usuario, prediction=prediction)

def predict_user_criticity(nombre, total, phishing, cliclados, method):
    con = sqlite3.connect('datos.db')
    cur = con.cursor()

    cur.execute("""
                SELECT nombre, telefono, provincia, permisos, total, phishing, cliclados
                FROM usuarios
                JOIN emails ON usuarios.nombre = emails.usuario
                WHERE usuarios.nombre = ?
            """, (nombre,))
    row = cur.fetchone()
    prediction = None
    if row:
        _, _, _, permisos_db, total_db, phishing_db, cliclados_db = row
        porcentaje_phishing_cliclados = (phishing_db / cliclados_db) * 100
        user_data = [[phishing_db, cliclados_db, total_db, permisos_db]]

        if method == 'Regresión Lineal':
            regr = load('linear_regression_model.joblib')
            prediction = regr.predict(user_data)
        elif method == 'Árbol de Decisión':
            clf_model = load('decision_tree_model.joblib')
            prediction = clf_model.predict(user_data)
        elif method == 'Bosque Aleatorio':
            clf = load('random_forest_model.joblib')
            prediction = clf.predict(user_data)

    con.close()
    return prediction
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


@app.route('/top_paginas_desactualizadas')
def top_paginas_desactualizadas():
    x = request.args.get('xWeb', default=5, type=int)
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT web FROM legal WHERE cookies > 0 OR aviso > 0 OR proteccion_de_datos > 0 ORDER BY (cookies + aviso + proteccion_de_datos), creacion LIMIT ?", (x,))
    paginas_desactualizadas = cur.fetchall()
    con.close()
    return render_template('paginas_desactualizadas.html', paginas_desactualizadas=paginas_desactualizadas)


@app.route('/top_paginas_desactualizadas_pdf')
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
    style_normal = styles['Normal']

    content = []
    content.append(Paragraph("Últimas Vulnerabilidades", styles['Title']))
    content.append(Paragraph("<br/><br/>", style_normal))

    column_widths = [1 * inch, 5 * inch]

    table_data = [["ID", "Descripción"]]
    for cve in cves:
        table_data.append([cve['id'], Paragraph(cve['summary'], style_normal)])

    t = Table(table_data, colWidths=column_widths)
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                           ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                           ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                           ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                           ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                           ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                           ('GRID', (0, 0), (-1, -1), 1, colors.black),
                           ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                           ('WORDWRAP', (1, 1), (-1, -1), True)]))

    content.append(t)
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


if __name__ == '__main__':
    app.run(debug = True)
