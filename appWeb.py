from flask import Flask, render_template

import ejercicio2
from ejercicio3 import prepareDf

app = Flask(__name__)
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


if __name__ == '__main__':
    app.run(debug = True)
