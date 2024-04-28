from sklearn import tree
from sklearn.datasets import load_iris
import graphviz #https://graphviz.org/download/

def perform_decision_tree():
    #Split data
    iris = load_iris()
    X, y = iris.data, iris.target
    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(X, y)
    return clf

def visualize_decision_tree(clf):
    #Print plot
    iris = load_iris()
    dot_data = tree.export_graphviz(clf, out_file=None,
                        feature_names=iris.feature_names,
                        class_names=iris.target_names,
                        filled=True, rounded=True,
                        special_characters=True)
    graph = graphviz.Source(dot_data)
    graph.render('test.gv', view=False).replace('\\', '/')


# Predict
clf_model = perform_decision_tree()
visualize_decision_tree(clf_model)
