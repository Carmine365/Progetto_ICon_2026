from seaborn import heatmap
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# 1. CAMBIO NOME FILE E TARGET
import os
DIABETES_DATA_FILE = os.path.join("data", "water_potability.csv")
TARGET = "Potability" # Nel CSV dell'acqua si chiama così, non "Outcome"

# Consiglio: Rinomina la classe in 'water_data' per coerenza, 
# ma ricorda di cambiare l'import anche nel main.py!
class water_data: 

    def __init__(self):
        # Carica e pulisce i dati (rimuove righe con campi vuoti)
        self.data = pd.read_csv(DIABETES_DATA_FILE).dropna()
        
        # 2. RIMOSSO 'del Pregnancies': Non serve, quella colonna non esiste qui.
        
        self.features_list = list(self.data.columns)

    def get_data(self):
        return self.data

    def get_features(self):
        return self.features_list

    def get_heatmap(self):
        plt.figure(figsize=(10, 8)) # Aggiunto per renderla leggibile
        heatmap(self.data.corr(), annot=True, fmt=".2f")
        plt.show()

    def plot_potability(self):
        plt.style.use("ggplot")
        # Qui usiamo il nome corretto della colonna
        self.data["Potability"].value_counts().plot.bar(
            title='Potability Distribution', rot=0)
        plt.show()

    def plot_ph(self):
        plt.style.use("ggplot")
        list_ph = []
        # IL pH va da 0 a 14. Il range(0,100,10) era troppo largo.
        # Lo cambio in range(0, 15, 1) per avere barre più sensate.
        for a in self.data["ph"]:
            for e in range(0, 15, 1): 
                if a >= e and a < (e+1): # Binning per unità
                    label = "%d-%d" % (e, (e+1))
                    list_ph.append(label)
        
        # Ordiniamo l'indice per avere il grafico sequenziale
        pd.DataFrame(list_ph).value_counts().sort_index().plot.bar(
            title='PH Distribution', rot=0)
        plt.show()

    def plot_hardness(self):
        plt.style.use("ggplot")
        list_hardness = []
        # La durezza va da circa 100 a 300. Adattiamo il range.
        for hardness in self.data["Hardness"]:
            for b in range(0, 350, 50): # Step di 50
                if hardness >= b and hardness < (b+50):
                    label = "%d-%d" % (b, (b+50))
                    list_hardness.append(label)
                    
        pd.DataFrame(list_hardness).value_counts().sort_index().plot.bar(
            title='Hardness Distribution', rot=45)
        plt.show()

    def get_training_data(self):
        y = self.data[[TARGET]].values
        x = self.data.drop(TARGET, axis='columns').values
        return x, y
    
    # 3. METODO CRUCIALE PER L'AGENTE INTELLIGENTE
    # Ho rinominato le chiavi con i parametri dell'acqua
    def get_medium_values_water(self): # Rinominalo anche dove viene chiamato!

        medium_values = {}
        # Prende solo i casi di acqua POTABILE (1)
        positives = self.data[self.data[TARGET] == 1]
        
        # Calcola le medie dei valori "buoni"
        # Queste chiavi devono corrispondere a quelle che userai nell'ontologia/Prolog
        medium_values['ph'] = positives['ph'].mean()
        medium_values['Hardness'] = positives['Hardness'].mean()
        medium_values['Solids'] = positives['Solids'].mean() # TDS
        medium_values['Chloramines'] = positives['Chloramines'].mean()
        medium_values['Turbidity'] = positives['Turbidity'].mean()

        return medium_values