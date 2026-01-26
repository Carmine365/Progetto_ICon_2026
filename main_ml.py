# CAMBIO IMPORT: Rinominare i file o le classi se necessario
from src.data_loader import water_data 
from src.ml_evaluation import *
from src.ml_models import *

print("--- CARICAMENTO DATASET ACQUA ---")
# Caricamento dati Acqua
data = water_data() 
default_test_size = 0.3  # 30% per il test è lo standard

# PLOTTING: Visualizzazioni iniziali
print("Generazione Heatmap...")
data.get_heatmap()

print("Generazione Grafico Distribuzione Potabilità...")
data.plot_potability() # Corretto: nel nuovo water_data si chiama così

# Visualizzazioni specifiche per l'acqua
print("Generazione grafici per pH e Durezza...")
data.plot_ph()       
data.plot_hardness() 

# 1. LOGISTIC REGRESSION
print("\n--- Logistic Regression: Predicting Potability ---")
# Nota: Usiamo la classe 'water_logistic_regression' definita in models.py
model_1 = water_logistic_regression(data, 100, default_test_size)
model_1.predict()

print("\nLogistic Regression metrics:")
model_1.print_metrics()
model_1.get_confusion_matrix()

print("\n" + "="*30 + "\n")

# 2. DECISION TREE
print("--- Decision Tree: Predicting Potability ---")
model_2 = water_decision_tree(data, 50, default_test_size)
model_2.predict()

print("Decision tree metrics:")
model_2.print_metrics()
model_2.get_confusion_matrix()

print("\n" + "="*30 + "\n")

# 3. KNN
print("--- KNN: Predicting Potability ---")
# K=21 è un buon punto di partenza
model_3 = water_knn(data, default_test_size, 21) 
model_3.predict()

print("KNN metrics:")
model_3.print_metrics()
model_3.get_confusion_matrix()

# CONFRONTO MODELLI (Grafici finali)
print("\n--- Generazione Grafici di Confronto ---")
metrics_graph_lr(data, default_test_size)
metrics_graph_dt(data, default_test_size)
metrics_graph_knn(data, default_test_size)
comparison_metrics_models(data, default_test_size)

print("\n--- ANALISI COMPLETATA ---")