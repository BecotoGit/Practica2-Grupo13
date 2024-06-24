import graphviz
import matplotlib.pyplot as plt
import pandas as pd
from sklearn import linear_model
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn import tree



def Linear_Regresion(X, y):
    X['cliclados'] = pd.to_numeric(X['cliclados'], errors='coerce')
    X['total'] = pd.to_numeric(X['total'], errors='coerce')
    X['permisos'] = pd.to_numeric(X['permisos'], errors='coerce')

    X_1dim = pd.DataFrame((X['cliclados'] / X['total']) * 0.75 + (X['permisos'] * 0.25))

    X_train, X_test, y_train, y_test = train_test_split(X_1dim, y, test_size=0.6, random_state=80)

    model = linear_model.LinearRegression()

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("Mean squared error: %.2f" % mean_squared_error(y_test, y_pred))

    plt.scatter(X_test, y_test, color="black")
    plt.plot(X_test, y_pred, color="blue", linewidth=3)
    plt.yticks([0, 1])
    plt.xlabel('(Clicados/Total) * 0.75 + Permisos * 0.25')
    plt.ylabel('Clasificación Usuario')
    plt.show()

    return model

def Regresion_Predict(model, nombre, telefono, provincia, permisos, total, phishing, cliclados):
    usuario = {
        'telefono': [telefono],
        'provincia': [provincia],
        'permisos': [permisos],
        'total': [total],
        'phishing': [phishing],
        'cliclados': [cliclados]
    }

    df_usuarios = pd.DataFrame(usuario)
    usuarios_1dim = pd.DataFrame((df_usuarios['cliclados'] / df_usuarios['total']) * 0.75 + (df_usuarios['permisos'] * 0.25))
    prediccion_nuevo = model.predict(usuarios_1dim)

    esCritico = True
    if prediccion_nuevo < model.coef_:
        esCritico = False

    return esCritico

def Arbol_Decision(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=75)

    clf = tree.DecisionTreeClassifier(random_state=20)
    clf = clf.fit(X_train, y_train)

    fig, ax = plt.subplots(figsize=(20, 10))
    tree.plot_tree(clf, feature_names=X.columns, class_names=['No Crítico', 'Crítico'], filled=True, rounded=True, ax=ax,
                   node_ids=True, fontsize=10)
    
    ax.annotate('True', xy=(0.25, 0.85), xycoords='axes fraction', fontsize=12, ha='center', va='center')
    ax.annotate('False', xy=(0.75, 0.85), xycoords='axes fraction', fontsize=12, ha='center', va='center')

    plt.show()

    return clf



def Arbol_Decision_Predict(clf, nombre, telefono, provincia, permisos, total, phishing, cliclados):
    usuario = {
        'telefono': [telefono],
        'provincia': [provincia],
        'permisos': [permisos],
        'total': [total],
        'phishing': [phishing],
        'cliclados': [cliclados]
    }

    df_usuario = pd.DataFrame(usuario)
    prediccion_nuevo = clf.predict(df_usuario)

    return prediccion_nuevo[0] 



def forest(X, y):

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.6, random_state=24)
    clf = RandomForestClassifier(max_depth=2, random_state=0, n_estimators=10)
    clf.fit(X_train, y_train)

    for i in range(len(clf.estimators_)):
        estimator = clf.estimators_[i]
        dot_data = tree.export_graphviz(estimator,
                                        out_file=None,
                                        feature_names=X.columns.values,
                                        class_names=['No Crítico', 'Crítico'],  
                                        rounded=True,
                                        proportion=False,
                                        precision=2,
                                        filled=True)
        graph = graphviz.Source(dot_data)
        graph.render('tree' + str(i))

    return clf


def Forest_Predict(clf, nombre, telefono, provincia, permisos, total, phishing, cliclados):
    usuario = {
        'telefono': [telefono],
        'provincia': [provincia],
        'permisos': [permisos],
        'total': [total],
        'phishing': [phishing],
        'cliclados': [cliclados]
    }

    df_usuario = pd.DataFrame(usuario)
    prediccion_nuevo = clf.predict(df_usuario)

    return prediccion_nuevo