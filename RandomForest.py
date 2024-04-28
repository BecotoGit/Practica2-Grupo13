from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import export_graphviz
from sklearn.datasets import load_iris
from subprocess import call
import graphviz #https://graphviz.org/download/
from os import path


def perform_random_forest():
    #Split data
    iris = load_iris()
    X, y = iris.data, iris.target
    clf = RandomForestClassifier(max_depth=2, random_state=0,n_estimators=10)
    clf.fit(X, y)

    for i, estimator in enumerate(clf.estimators_):
        export_graphviz(estimator,
                        out_file=path.join('static', f'tree_{i}.dot'),
                        feature_names=iris.feature_names,
                        class_names=iris.target_names,
                        rounded=True, proportion=False,
                        precision=2, filled=True)
        call(['dot', '-Tpng', f'tree_{i}.dot', '-o', f'tree_{i}.png', '-Gdpi=600'])
