import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
from joblib import dump
import sqlite3
import os


conn = sqlite3.connect('datos.db')
cur = conn.cursor()

cur.execute("""
    SELECT phishing, cliclados, critico
    FROM usuarios
    JOIN emails ON usuarios.nombre = emails.usuario
    WHERE critico = 1
""")
train_data = cur.fetchall()

cur.execute("""
    SELECT phishing, cliclados, critico
    FROM usuarios
    JOIN emails ON usuarios.nombre = emails.usuario
    WHERE critico = 0
""")
test_data = cur.fetchall()

conn.close()

phishing_cliclados_train = [row[0] for row in train_data]
y_train = [row[2] for row in train_data]

phishing_cliclados_test = [row[0] for row in test_data]
y_test = [row[2] for row in test_data]

X_train = np.array(phishing_cliclados_train).reshape(-1, 1)
X_test = np.array(phishing_cliclados_test).reshape(-1, 1)

regr = linear_model.LinearRegression()

regr.fit(X_train, y_train)

dump(regr, 'linear_regression_model.joblib')

print("Coeficiente del modelo:", regr.coef_)

y_pred = regr.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
print("Mean Squared Error:", mse)

plt.scatter(X_test, y_test, color="black")
plt.plot(X_test, y_pred, color="blue", linewidth=3)
plt.xlabel("Porcentaje de Phishing/Cliclados")
plt.ylabel("Crítico (1) / No Crítico (0)")
plt.title("Predicciones vs. Valores Verdaderos")
plt.xticks(())
plt.yticks(())
output_dir = 'static/'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_file = os.path.join(output_dir, 'linear_regression_plot.png')
plt.savefig(output_file)
plt.show()
