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

if __name__ == "__main__":
    
    # 1. Caricamento Dati
    print("--- 1. Caricamento Dataset Acqua ---")
    data = water_data()
    print("Dataset caricato correttamente.")
    
    # 2. Addestramento Modelli Classici
    print("\n--- 2. Esecuzione Modelli Classici (LogReg, DT, KNN) ---")
    
    # Logistic Regression
    print("\n[Logistic Regression]")
    log_reg = water_log_reg(data, 0.2)
    log_reg.predict()
    log_reg.print_metrics()
    
    # Decision Tree
    print("\n[Decision Tree]")
    dec_tree = water_dec_tree(data, 0.2)
    dec_tree.predict()
    dec_tree.print_metrics()
    
    # KNN
    print("\n[K-Nearest Neighbors]")
    knn = water_knn(data, 0.2, 5)
    knn.predict()
    knn.print_metrics()
    
    # 3. Addestramento Nuovi Modelli (Per Copertura Teoria ICon)
    print("\n--- 3. Esecuzione Modelli Avanzati (Reti Neurali & Incertezza) ---")
    
    # Rete Neurale (Capitolo 8)
    print("\n[Neural Network - MLPClassifier]")
    print("Architettura: Input -> Hidden(64) -> Hidden(32) -> Output")
    nn = water_neural_network(data, 0.2)
    nn.predict()
    nn.print_metrics()
    
    # Naive Bayes (Capitolo 9 - Ragionamento Probabilistico)
    print("\n[Naive Bayes - GaussianNB]")
    print("Modello Probabilistico basato sul Teorema di Bayes")
    nb = water_naive_bayes(data, 0.2)
    nb.predict()
    nb.print_metrics()
    
    print("\n--- Analisi Completata ---")