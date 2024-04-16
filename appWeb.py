from flask import Flask, render_template

import ejercicio2

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
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
    usuarios_df, emails_df, legal_df = ejercicio2.obtener_datos()

    n_muestras = ejercicio2.num_muestras(usuarios_df)
    media_fechas, desviacion_fechas = ejercicio2.mean_std_fechas(usuarios_df)
    media_ips, desviacion_ips = ejercicio2.mean_std_ips(usuarios_df)
    media, desviacion_estandar = ejercicio2.mean_std_emails()
    minimo, maximo = ejercicio2.minMax_emails()
    minimo_admin, maximo_admin = ejercicio2.minMax_phish_admin()
    return render_template('ej2.html', num_muestras=n_muestras, media_fechas=media_fechas,
                           desviacion_fechas=desviacion_fechas, media_ips=media_ips, desviacion_ips=desviacion_ips,
                           media=media, desviacion_estandar=desviacion_estandar, minimo=minimo, maximo=maximo,
                           minimo_admin=minimo_admin, maximo_admin=maximo_admin)

@app.route('ej3')
def ej3():


 if __name__ == '__main__':
    app.run(debug = True)



