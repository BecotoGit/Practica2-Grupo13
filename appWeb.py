import sqlite3
import requests
from flask import Flask, render_template, request, make_response
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO


app = Flask(__name__)
def connect_db():
    return sqlite3.connect('datos.db')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analizar_usuario')
def analizar_usuario():
    # Obtener datos del formulario
    name = request.form['name']
    phone = request.form['phone']
    province = request.form['province']
    permissions = request.form['permissions']
    total_sent_emails = request.form['total_sent_emails']
    total_phishing_emails = request.form['total_phishing_emails']
    total_clicked_emails = request.form['total_clicked_emails']
    method = request.form['method']

    # Preparar datos del usuario nuevo
    user_data = (name, phone, province, permissions, total_sent_emails, total_phishing_emails, total_clicked_emails)

    # Utilizar el método de IA seleccionado para predecir si el usuario es crítico o no
    prediction = predict_user_criticity(user_data, method)

    # Mostrar resultado en la interfaz de usuario
    return render_template('resultado_analisis.html', prediction=prediction)

def predict_user_criticity(user_data, method):
    con = sqlite3.connect('datos.db')
    cur = con.cursor()
    if method == 'Regresión Lineal':
        prediction = predict_using_linear_regression(user_data)
    elif method == 'Árbol de Decisión':
        prediction = predict_using_decision_tree(user_data)
    elif method == 'Bosque Aleatorio':
        prediction = predict_using_random_forest(user_data)
    con.close()

    return prediction

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

@app.route('/top_usuarios_criticos_pdf')
def top_usuarios_criticos_pdf():
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

    # Define el ancho de cada columna
    column_widths = [1 * inch, 5 * inch]  # Ancho en pulgadas

    table_data = [["ID", "Descripción"]]
    for cve in cves:
        table_data.append([cve['id'], Paragraph(cve['summary'], style_normal)])

    # Crea la tabla con los anchos de columna definidos
    t = Table(table_data, colWidths=column_widths)
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                           ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                           ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                           ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                           ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                           ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                           ('GRID', (0, 0), (-1, -1), 1, colors.black),
                           ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                           ('WORDWRAP', (1, 1), (-1, -1), True)]))  # Permitir el ajuste de texto en varias líneas en la columna de descripción

    content.append(t)

    doc.build(content)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data



if __name__ == '__main__':
    app.run(debug = True)
