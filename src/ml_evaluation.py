from src.ml_models import *
from numpy import linspace
import matplotlib.pyplot as plt

from .data_loader import waterData 

def get_linspace(start: int, end: int, step: int):
    linspace_vect = []
    for i in range(start, end, step):
        linspace_vect.append(i)
    return linspace_vect


def metrics_graph_lr(data: waterData, test_size: float):

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
        model_i = waterLogReg(
            data, int(iterations_vect[i]), test_size)

        model_i.predict()

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


def metrics_graph_dt(data: waterData, test_size: float):

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
        model_i = waterDecTree(data, iterations_vect[i], test_size)

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


def metrics_graph_knn(data: waterData, test_size: float):

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
        model_i = waterKnn(data, test_size, iterations_vect[i])

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

def comparison_metrics_models(data: waterData, test_size: float):
    print("\n--- AVVIO VALUTAZIONE COMPARATIVA (Cross-Validation) ---")
    
    # 1. Istanziamo i modelli (usando i nomi corretti presenti nel tuo ml_models.py)
    # Nota: per la CV il test_size nel costruttore è meno rilevante, ma lo passiamo per compatibilità
    models = {
        "Logistic Regression": waterLogReg(data, test_size),
        "Decision Tree": waterDecTree(data, test_size),
        "KNN": waterKnn(data, test_size, neighbors=9),
        "Neural Network": waterNeuralNetwork(data, test_size), # Bonus Cap. 8
        "Naive Bayes": waterNaiveBayes(data, test_size)        # Bonus Cap. 9
    }

    # Strutture dati per il plot
    metric_names = ['Accuracy', 'Precision', 'Recall', 'F1']

    # Dizionario che conterrà liste di valori per ogni metrica: {'Accuracy': [val_mod1, val_mod2...], ...}
    means_by_metric = {m: [] for m in metric_names}
    stds_by_metric = {m: [] for m in metric_names}
    model_names = []

    # --- INIZIO HEADER TABELLA ---
    print("\n" + "="*85)
    print(f"{'MODELLO':<25} | {'ACCURACY (Mean ± Std)':<22} | {'PRECISION':<10} | {'RECALL':<10} | {'F1':<10}")
    print("-" * 85)
    # -----------------------------

    # 2. Calcolo Metriche e Stampa
    for name, model in models.items():
        # Calcoliamo le metriche
        means, stds = model.evaluate_with_cross_validation(folds=10)
        
        # Salviamo per il grafico
        model_names.append(name)
        for m in metric_names:
            means_by_metric[m].append(means[m])
            stds_by_metric[m].append(stds[m])

        # --- STAMPA RIGA TABELLA ---
        # Formattiamo i numeri: .3f significa "3 cifre decimali"
        print(f"{name:<25} | {means['Accuracy']:.3f} ± {stds['Accuracy']:.3f}        | "
              f"{means['Precision']:.3f}      | {means['Recall']:.3f}      | {means['F1']:.3f}")
    
    print("="*85 + "\n")

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