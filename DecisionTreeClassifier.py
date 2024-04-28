from sklearn import tree
from sklearn.datasets import load_iris
import graphviz #https://graphviz.org/download/
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

conn.close()

X_train = [data[:2] for data in train_data]
y_train = [data[2] for data in train_data]

clf = tree.DecisionTreeClassifier()
clf = clf.fit(X_train, y_train)

dump(clf, 'decision_tree_model.joblib')

dot_data = tree.export_graphviz(clf, out_file=None,
                                feature_names=['phishing', 'cliclados'],
                                class_names=['No Crítico', 'Crítico'],
                                filled=True,
                                rounded=True,
                                special_characters=True)

output_dir = 'static/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_dot_file = os.path.join(output_dir, 'decision_tree.dot')
with open(output_dot_file, 'w') as f:
    f.write(dot_data)

output_image_file = os.path.join(output_dir, 'decision_tree.png')

graph = graphviz.Source(dot_data)
graph.render('decision_tree', view=True)

