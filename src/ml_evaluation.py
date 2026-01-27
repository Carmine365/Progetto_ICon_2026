from src.ml_models import *
from numpy import linspace
import matplotlib.pyplot as plt
# IMPORT CORRETTO: Assicurati che water_data.py contenga la classe water_data
from .data_loader import water_data 

def get_linspace(start: int, end: int, step: int):
    linspace_vect = []
    for i in range(start, end, step):
        linspace_vect.append(i)
    return linspace_vect


def metrics_graph_lr(data: water_data, test_size: float):

    # Riduco un po' i punti per rendere il calcolo più veloce (da 100 a 20)
    iterations_vect = linspace(10, 200, 20) 
    precision_vect = []
    recall_vect = []
    f1_score_vect = []
    accuracy_vect = []

    a, graph_lr = plt.subplots(4, 1, figsize=(8, 12)) # Aumentata dimensione per leggibilità
    a.tight_layout(pad=5.0)

    i = 0
    while i < len(iterations_vect):
        # CAMBIO NOME CLASSE
        model_i = water_log_reg(
            data, int(iterations_vect[i]), test_size)

        model_i.predict()
        # CORREZIONE KEY: "Accuracy" invece di "Accurancy"
        accuracy_vect.append(model_i.get_metric("Accuracy"))
        precision_vect.append(model_i.get_metric("Precision"))
        recall_vect.append(model_i.get_metric("Recall"))
        f1_score_vect.append(model_i.get_metric("F1_precision"))

        i = i + 1

    graph_lr[0].plot(iterations_vect, accuracy_vect, color='blue')
    graph_lr[0].set_title("Accuracy - Logistic Regression")

    graph_lr[1].plot(iterations_vect, precision_vect, color='orange')
    graph_lr[1].set_title("Precision - Logistic Regression")

    graph_lr[2].plot(iterations_vect, recall_vect, color='green')
    graph_lr[2].set_title("Recall - Logistic Regression")

    graph_lr[3].plot(iterations_vect, f1_score_vect, color='red')
    graph_lr[3].set_title("F1_Precision - Logistic Regression")

    plt.show()


def metrics_graph_dt(data: water_data, test_size: float):

    # Depth dell'albero da 1 a 20
    iterations_vect = get_linspace(1, 20, 1) 
    precision_vect = []
    recall_vect = []
    f1_score_vect = []
    accuracy_vect = []

    a, graph_lr = plt.subplots(2, 2, figsize=(10, 8))
    a.tight_layout(pad=4.0)

    i = 0
    while i < len(iterations_vect):
        # CAMBIO NOME CLASSE
        model_i = water_dec_tree(data, iterations_vect[i], test_size)

        model_i.predict()
        accuracy_vect.append(model_i.get_metric("Accuracy"))
        precision_vect.append(model_i.get_metric("Precision"))
        recall_vect.append(model_i.get_metric("Recall"))
        f1_score_vect.append(model_i.get_metric("F1_precision"))

        i = i + 1

    graph_lr[0, 0].plot(iterations_vect, accuracy_vect, color='blue')
    graph_lr[0, 0].set_title("Accuracy - Decision Tree")

    graph_lr[0, 1].plot(iterations_vect, precision_vect, color='orange')
    graph_lr[0, 1].set_title("Precision - Decision Tree")

    graph_lr[1, 0].plot(iterations_vect, recall_vect, color='green')
    graph_lr[1, 0].set_title("Recall - Decision Tree")

    graph_lr[1, 1].plot(iterations_vect, f1_score_vect, color='red')
    graph_lr[1, 1].set_title("F1_Precision - Decision Tree")
    plt.show()


def metrics_graph_knn(data: water_data, test_size: float):

    # Neighbors da 1 a 50
    iterations_vect = get_linspace(1, 50, 2)
    precision_vect = []
    recall_vect = []
    f1_score_vect = []
    accuracy_vect = []

    a, graph_lr = plt.subplots(2, 2, figsize=(10, 8))
    a.tight_layout(pad=4.0)

    i = 0
    while i < len(iterations_vect):
        # CAMBIO NOME CLASSE
        model_i = water_knn(data, test_size, iterations_vect[i])

        model_i.predict()
        accuracy_vect.append(model_i.get_metric("Accuracy"))
        precision_vect.append(model_i.get_metric("Precision"))
        recall_vect.append(model_i.get_metric("Recall"))
        f1_score_vect.append(model_i.get_metric("F1_precision"))

        i = i + 1

    graph_lr[0, 0].plot(iterations_vect, accuracy_vect, color='blue')
    graph_lr[0, 0].set_title("Accuracy - KNN")

    graph_lr[0, 1].plot(iterations_vect, precision_vect, color='orange')
    graph_lr[0, 1].set_title("Precision - KNN")

    graph_lr[1, 0].plot(iterations_vect, recall_vect, color='green')
    graph_lr[1, 0].set_title("Recall - KNN")

    graph_lr[1, 1].plot(iterations_vect, f1_score_vect, color='red')
    graph_lr[1, 1].set_title("F1_Precision - KNN")
    plt.show()

"""
def comparison_metrics_models(data: water_data, test_size: float):

    # CAMBIO NOMI CLASSI
    model_1 = water_logistic_regression(data, 100, test_size)
    model_1.predict()

    model_2 = water_decision_tree(data, 10, test_size) # Depth ragionevole
    model_2.predict()

    model_3 = water_knn(data, test_size, 21)
    model_3.predict()

    a, graph_lr = plt.subplots(2, 2, figsize=(10, 8))
    a.tight_layout(pad=4.0)

    precision_data_dict = {
        "Logistic_Reg": model_1.get_metric("Precision"), 
        "Decision_Tree": model_2.get_metric("Precision"), 
        "KNN": model_3.get_metric("Precision")
    }

    recall_data_dict = {
        "Logistic_Reg": model_1.get_metric("Recall"), 
        "Decision_Tree": model_2.get_metric("Recall"), 
        "KNN": model_3.get_metric("Recall")
    }

    f1_data_dict = {
        "Logistic_Reg": model_1.get_metric("F1_precision"), 
        "Decision_Tree": model_2.get_metric("F1_precision"), 
        "KNN": model_3.get_metric("F1_precision")
    }

    accuracy_data_dict = {
        "Logistic_Reg": model_1.get_metric("Accuracy"), 
        "Decision_Tree": model_2.get_metric("Accuracy"), 
        "KNN": model_3.get_metric("Accuracy")
    }

    models_names = list(precision_data_dict.keys())

    models_precision_data = list(precision_data_dict.values())
    models_recall_data = list(recall_data_dict.values())
    models_f1_data = list(f1_data_dict.values())
    models_accuracy_data = list(accuracy_data_dict.values())

    graph_lr[0, 0].bar(models_names, models_precision_data, color="red")
    graph_lr[0, 0].set_title("Precision")

    graph_lr[0, 1].bar(models_names, models_recall_data, color="green")
    graph_lr[0, 1].set_title("Recall")

    graph_lr[1, 0].bar(models_names, models_f1_data, color="purple")
    graph_lr[1, 0].set_title("F1-precision")

    graph_lr[1, 1].bar(models_names, models_accuracy_data, color="blue")
    graph_lr[1, 1].set_title("Accuracy")

    plt.show()
"""
def comparison_metrics_models(data: water_data, test_size: float):
    print("\n--- AVVIO VALUTAZIONE COMPARATIVA (Cross-Validation) ---")
    
    # 1. Istanziamo i modelli (usando i nomi corretti presenti nel tuo ml_models.py)
    # Nota: per la CV il test_size nel costruttore è meno rilevante, ma lo passiamo per compatibilità
    models = {
        "Logistic Regression": water_log_reg(data, test_size),
        "Decision Tree": water_dec_tree(data, test_size),
        "KNN": water_knn(data, test_size, neighbors=9),
        "Neural Network": water_neural_network(data, test_size), # Bonus Cap. 8
        "Naive Bayes": water_naive_bayes(data, test_size)        # Bonus Cap. 9
    }

    # Strutture dati per il plot
    metric_names = ['Accuracy', 'Precision', 'Recall', 'F1']
    # Dizionario che conterrà liste di valori per ogni metrica: {'Accuracy': [val_mod1, val_mod2...], ...}
    means_by_metric = {m: [] for m in metric_names}
    stds_by_metric = {m: [] for m in metric_names}
    model_names = []

    # 2. Calcolo Metriche
    for name, model in models.items():
        print(f"Valutazione {name}...")
        means, stds = model.evaluate_with_cross_validation(folds=10)
        
        model_names.append(name)
        for m in metric_names:
            means_by_metric[m].append(means[m])
            stds_by_metric[m].append(stds[m])

    # 3. Creazione Grafico Raggruppato
    x = np.arange(len(model_names))  # Posizioni sull'asse X
    width = 0.2  # Larghezza delle barre
    multiplier = 0

    fig, ax = plt.subplots(figsize=(14, 7))

    for attribute, measurement in means_by_metric.items():
        offset = width * multiplier
        # Disegna le barre per questa metrica (es. Accuracy) per tutti i modelli
        rects = ax.bar(x + offset, measurement, width, yerr=stds_by_metric[attribute], 
                       label=attribute, capsize=4)
        multiplier += 1

    # Personalizzazione Grafico
    ax.set_ylabel('Punteggio (0-1)')
    ax.set_title('Confronto Completo Modelli (Media CV ± Dev.Std)')
    ax.set_xticks(x + width * 1.5) # Centra le etichette
    ax.set_xticklabels(model_names)
    ax.legend(loc='lower right', ncols=4)
    ax.set_ylim(0, 1.1)
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    plt.tight_layout()
    plt.show()