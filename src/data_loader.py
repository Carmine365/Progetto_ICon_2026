from seaborn import heatmap, histplot, countplot
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

# 1. CAMBIO NOME FILE E TARGET
# --- 1. FIX PERCORSO ASSOLUTO ---
# Calcola il percorso base partendo dalla posizione di QUESTO file (src/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WATER_DATA_FILE = os.path.join(BASE_DIR, "data", "water_potability.csv")
TARGET = "Potability"

class waterData: 

    def __init__(self):
        # Carica e pulisce i dati (rimuove righe con campi vuoti)
        self.data = pd.read_csv(WATER_DATA_FILE)
        
        # --- CORREZIONE: RIMOSSO IL DATA LEAKAGE ---
        # Lasciamo i NaN.
        # Saranno gestiti dalla Pipeline di scikit-learn dentro ml_models.py
        # self.data.fillna(self.data.mean(), inplace=True) <--- RIMOSSO
        
        self.features_list = list(self.data.columns)

    def get_data(self):
        return self.data

    def get_features(self):
        return self.features_list

    def get_heatmap(self):
        """Genera una heatmap della correlazione più leggibile."""
        plt.figure(figsize=(10, 8))
        # numeric_only=True evita errori futuri con versioni nuove di Pandas
        corr = self.data.corr(numeric_only=True)
        heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", cbar=True)
        plt.title("Matrice di Correlazione tra Feature")
        plt.show()

    def plot_potability(self):
        """Grafico a barre della distribuzione della target variable."""
        plt.figure(figsize=(6, 4))
        plt.style.use("ggplot")
        
        # Uso countplot di Seaborn: fa tutto da solo (conteggi e colori)
        ax = countplot(x=TARGET, data=self.data, palette="viridis")
        ax.set_title("Distribuzione Potabilità (0=Non Potabile, 1=Potabile)")
        ax.set_xlabel("Classe")
        ax.set_ylabel("Conteggio")
        
        # Aggiunge le etichette con i numeri sopra le barre
        for p in ax.patches:
            ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='center', xytext=(0, 5), textcoords='offset points')
        plt.show()

    def plot_ph(self):
        """Istogramma della distribuzione del pH."""
        plt.figure(figsize=(8, 5))
        plt.style.use("ggplot")
        
        # Sostituisce il vecchio ciclo for manuale con histplot nativo ottimizzato
        # kde=True aggiunge la curva di densità smussata
        histplot(data=self.data, x="ph", bins=30, kde=True, color="purple")
        
        plt.title("Distribuzione del pH")
        plt.xlabel("Valore pH (0-14)")
        plt.ylabel("Frequenza")
        plt.xlim(0, 14) # Forza i limiti fisici della scala del pH
        plt.show()

    def plot_hardness(self):
        """Istogramma della Durezza."""
        plt.figure(figsize=(8, 5))
        plt.style.use("ggplot")
        
        histplot(data=self.data, x="Hardness", bins=30, kde=True, color="blue")
        
        plt.title("Distribuzione della Durezza (Hardness)")
        plt.xlabel("mg/L")
        plt.show()

    def get_training_data(self):
        """Restituisce X e y per il training."""
        y = self.data[[TARGET]].values
        x = self.data.drop(TARGET, axis='columns').values
        return x, y
    
    # 3. METODO CRUCIALE PER L'AGENTE INTELLIGENTE
    def get_medium_values_water(self):
        """
        Calcola le medie per i campioni POTABILI (Target=1).
        Metodo cruciale usato dal Sistema Esperto.
        """
        medium_values = {}
        
        # Filtriamo solo i campioni potabili
        positives = self.data[self.data[TARGET] == 1]
        
        # Pandas .mean() gestisce i NaN automaticamente, quindi non serve pulire prima.
        # Le chiavi devono corrispondere ai nomi usati nell'ontologia e nel sistema esperto.
        medium_values['ph'] = positives['ph'].mean()
        medium_values['Hardness'] = positives['Hardness'].mean()
        medium_values['Solids'] = positives['Solids'].mean()
        medium_values['Chloramines'] = positives['Chloramines'].mean()
        medium_values['Sulfate'] = positives['Sulfate'].mean()
        medium_values['Conductivity'] = positives['Conductivity'].mean()
        medium_values['Organic_carbon'] = positives['Organic_carbon'].mean()
        medium_values['Trihalomethanes'] = positives['Trihalomethanes'].mean()
        medium_values['Turbidity'] = positives['Turbidity'].mean()

        return medium_values