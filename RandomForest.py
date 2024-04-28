from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import export_graphviz
from sklearn.datasets import load_iris
from subprocess import call
from joblib import dump
import graphviz #https://graphviz.org/download/
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

conn.close()

X_train = [data[:2] for data in train_data]
y_train = [data[2] for data in train_data]

clf = RandomForestClassifier(max_depth=2, random_state=0, n_estimators=10)
clf.fit(X_train, y_train)

dump(clf, 'random_forest_model.joblib')

output_dir = 'static/'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for i, estimator in enumerate(clf.estimators_):
    output_file = os.path.join(output_dir, f'tree_{i}.dot')
    export_graphviz(estimator,
                    out_file=output_file,
                    feature_names=['phishing', 'cliclados'],
                    class_names=['No Crítico', 'Crítico'],
                    rounded=True,
                    proportion=False,
                    precision=2,
                    filled=True)



