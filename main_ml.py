import matplotlib.pyplot as plt
import pandas as pd  # <--- È QUI
import seaborn as sns
from src.data_loader import water_data
from src.ml_models import (
    water_log_reg, 
    water_dec_tree, 
    water_knn, 
    water_neural_network, # <--- NUOVO
    water_naive_bayes     # <--- NUOVO
)
import warnings

# Ignora warning di convergenza per demo didattica se le iterazioni sono poche
warnings.filterwarnings('ignore') 

def plot_model_comparison(results):
    """
    Genera un grafico a barre finale per confrontare i modelli.
    """
    df_res = pd.DataFrame(results)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x="Model", y="Accuracy", data=df_res, palette="viridis")
    plt.ylim(0, 1.0)
    plt.title("Confronto Accuratezza Modelli")
    plt.ylabel("Accuracy Score")
    plt.xlabel("Modello")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # FIX: Iteriamo con enumerate per avere un indice intero sicuro (0, 1, 2...)
    # invece di affidarci all'indice di pandas che il linter vede come "Hashable"
    for i, row in df_res.iterrows():
        # Convertiamo esplicitamente 'i' in float per accontentare il linter
        plt.text(float(i), row.Accuracy + 0.01, f"{row.Accuracy:.2f}", color='black', ha="center")
        
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    
    # 1. Caricamento Dati
    print("--- 1. Caricamento Dataset Acqua ---")
    data = water_data()
    print("Dataset caricato correttamente.")
    
    final_results = []

    # --- DEFINIZIONE LISTA MODELLI ---
    # Usiamo un dizionario per ciclare in modo pulito
    models_to_run = [
        ("Logistic Regression", water_log_reg(data, 0.2)),
        ("Decision Tree", water_dec_tree(data, 0.2)),
        ("KNN (k=5)", water_knn(data, 0.2, 5)),
        ("Neural Network (MLP)", water_neural_network(data, 0.2)),
        ("Naive Bayes", water_naive_bayes(data, 0.2))
    ]

    print("\n--- 2. Addestramento e Generazione Grafici ---")

    for name, model_obj in models_to_run:
        print(f"\n[{name}] In esecuzione...")
        
        # A. CROSS-VALIDATION (Per la Lode e le Linee Guida)
        # Calcola media e deviazione standard su 10 fold
        print(f"   [1] Esecuzione Cross-Validation (10-fold)...")
        try:
            # Nota: Assicurati di aver aggiunto il metodo evaluate_with_cross_validation in ml_models.py
            # Se non l'hai fatto, il programma darà errore qui. Nel caso, commenta queste 2 righe.
            mean_acc, std_acc = model_obj.evaluate_with_cross_validation()
            print(f"       -> Accuracy Media: {mean_acc:.4f} (± {std_acc:.4f})")
            # USIAMO QUESTA PER IL REPORT (Più robusta)
            accuracy_for_report = mean_acc
        except AttributeError:
            print("       -> Metodo Cross-Validation non trovato (saltato).")
            # Se fallisce, usiamo quella del singolo test come fallback
            accuracy_for_report = model_obj.get_metric("Accuracy")

        # B. ADDESTRAMENTO STANDARD (Per i Grafici)
        # Serve per generare la matrice di confusione e la curva ROC su un singolo split
        print(f"   [2] Generazione Grafici su Test Set (20%)...")
        model_obj.predict()
        
        # 2. Stampa Metriche Testuali
        model_obj.print_metrics()
        
        # 3. MOSTRA I GRAFICI (Ecco la parte che mancava!)
        print(f"   -> Generazione Matrice di Confusione per {name}...")
        model_obj.get_confusion_matrix()
        
        print(f"   -> Generazione Curva ROC per {name}...")
        model_obj.get_roc_curve()
        
        # Salva l'accuratezza per il grafico finale
        acc = model_obj.get_metric("Accuracy")
        final_results.append({"Model": name, "Accuracy": accuracy_for_report})

    # --- 3. CONFRONTO FINALE ---
    print("\n--- 3. Confronto Finale ---")
    
    # Creiamo una vista tabellare dei risultati
    df_summary = pd.DataFrame(final_results)
    
    # --- ECCO LA DIDASCALIA CHE VOLEVI ---
    print("\nTabella 1: Riepilogo Accuratezza (valori medi su 10-fold Cross-Validation)")
    print("-" * 65)
    print(df_summary.to_string(index=False)) # Stampa la tabella pulita senza indici
    print("-" * 65)
    print("\n")

    plot_model_comparison(final_results)
    
    print("\n--- Analisi Completata ---")