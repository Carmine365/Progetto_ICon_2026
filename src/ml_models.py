from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier  # Cap. 8
from sklearn.naive_bayes import GaussianNB        # Cap. 9-10
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score,
                             confusion_matrix, f1_score, precision_score,
                             recall_score, roc_curve, auc)
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn import tree
import matplotlib.pyplot as plt
from typing import Final, Optional
import numpy as np

# Assicurati che l'import sia relativo se sei dentro il package src
from .data_loader import water_data 

class water_model:

    def __init__(self, model, x, y, scores_dict: dict, test_size: float):

        default_test_size: Final = 0.2  # 20% test è standard
        if not (0 < test_size < 1):
            test_size = default_test_size

        self.model = model
        self.x = x
        self.y = y
        self.scores = scores_dict
        self.test_size = test_size
        
        self.target = "Potability"

        # --- FIX: Inizializzazione variabili per evitare errori "Unknown" ---
        self.x_train = None
        self.x_test = None
        self.y_train = None
        self.y_test = None
        self.y_predicted = None
        # ------------------------------------------------------------------

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_metric(self, score_label: str):
        score_val = None
        if score_label in self.scores.keys():
            score_val = self.scores[score_label]
        return score_val

    def print_metrics(self):
        for s in self.scores.keys():
            print(s + ": " + str(self.scores[s]))
            
    def get_confusion_matrix(self):
        if self.y_test is not None and self.y_predicted is not None:
            cm = confusion_matrix(self.y_test, self.y_predicted)
            disp = ConfusionMatrixDisplay(confusion_matrix=cm)
            disp.plot()
            plt.title(f'Confusion Matrix - {self.__class__.__name__}')
            plt.show()
        else:
            print("Errore: Impossibile generare matrice, predizione mancante.")

    def get_roc_curve(self):
        if hasattr(self.model, "predict_proba") and self.x_test is not None:
            # Gestione sicura per modelli che supportano probabilità
            try:
                y_probs = self.model.predict_proba(self.x_test)[:, 1]
                fpr, tpr, _ = roc_curve(self.y_test, y_probs)
                roc_auc = auc(fpr, tpr)
                
                plt.figure()
                plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
                plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
                plt.xlim([0.0, 1.0])
                plt.ylim([0.0, 1.05])
                plt.xlabel('False Positive Rate')
                plt.ylabel('True Positive Rate')
                plt.title(f'ROC Curve - {self.__class__.__name__}')
                plt.legend(loc="lower right")
                plt.show()
            except Exception as e:
                print(f"Errore generazione ROC: {e}")
        else:
            print("Questo modello non supporta la curva ROC (manca predict_proba)")

    def __check_test_size(self, test_size):
        if test_size > 0 and test_size < 1:
            return True
        return False

    def evaluate_with_cross_validation(self, folds=10):
        """
        Esegue la Cross-Validation per soddisfare i requisiti delle Linee Guida.
        Calcola Media e Deviazione Standard invece di un singolo run.
        """
        # Eseguiamo 10 run diversi su porzioni diverse del dataset
        scores = cross_val_score(self.model, self.x, self.y.ravel(), cv=folds, scoring='accuracy')
        
        mean_acc = scores.mean()
        std_acc = scores.std()
        
        self.scores["CV_Mean_Accuracy"] = mean_acc
        self.scores["CV_Std_Dev"] = std_acc
        
        print(f"   [Cross-Validation {folds}-fold] Accuracy Media: {mean_acc:.4f} (+/- {std_acc:.4f})")
        return mean_acc, std_acc


class water_log_reg(water_model):
    def __init__(self, data: water_data, test_size: float):
        x, y = data.get_training_data()
        water_model.__init__(self, LogisticRegression(max_iter=1000), x, y, {}, test_size)
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(
            self.x, self.y, test_size=self.test_size)

    def predict(self):
        scaler = StandardScaler()
        self.x_train = scaler.fit_transform(self.x_train)
        self.x_test = scaler.transform(self.x_test) # FIX: Use transform on test

        self.model.fit(self.x_train, self.y_train.ravel())
        self.y_predicted = self.model.predict(self.x_test)

        self._calculate_scores()

    def _calculate_scores(self):
        self.scores["Accuracy"] = accuracy_score(self.y_test, self.y_predicted)
        self.scores["Precision"] = precision_score(self.y_test, self.y_predicted)
        self.scores["Recall"] = recall_score(self.y_test, self.y_predicted)
        self.scores["F1_precision"] = f1_score(self.y_test, self.y_predicted)


class water_dec_tree(water_model):
    def __init__(self, data: water_data, test_size: float):
        x, y = data.get_training_data()
        water_model.__init__(self, tree.DecisionTreeClassifier(), x, y, {}, test_size)
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(
            self.x, self.y, test_size=self.test_size)

    def predict(self):
        self.model.fit(self.x_train, self.y_train.ravel())
        self.y_predicted = self.model.predict(self.x_test)
        self._calculate_scores()

    def _calculate_scores(self):
        self.scores["Accuracy"] = accuracy_score(self.y_test, self.y_predicted)
        self.scores["Precision"] = precision_score(self.y_test, self.y_predicted)
        self.scores["Recall"] = recall_score(self.y_test, self.y_predicted)
        self.scores["F1_precision"] = f1_score(self.y_test, self.y_predicted)


class water_knn(water_model):
    def __init__(self, data: water_data, test_size: float, neighbors: int):
        x, y = data.get_training_data()
        self.neighbors = neighbors
        water_model.__init__(self, KNeighborsClassifier(n_neighbors=self.neighbors), x, y, {}, test_size)
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(
            self.x, self.y, test_size=self.test_size)

    def predict(self):
        scaler = StandardScaler()
        self.x_train = scaler.fit_transform(self.x_train)
        self.x_test = scaler.transform(self.x_test) # FIX: Use transform on test

        self.model.fit(self.x_train, self.y_train.ravel())
        self.y_predicted = self.model.predict(self.x_test)
        self._calculate_scores()

    def _calculate_scores(self):
        self.scores["Accuracy"] = accuracy_score(self.y_test, self.y_predicted)
        self.scores["Precision"] = precision_score(self.y_test, self.y_predicted)
        self.scores["Recall"] = recall_score(self.y_test, self.y_predicted)
        self.scores["F1_precision"] = f1_score(self.y_test, self.y_predicted)


# --- NUOVI MODELLI PER COPERTURA TEORICA ---

class water_neural_network(water_model):
    """ Implementazione Rete Neurale (Cap. 8) """
    def __init__(self, data: water_data, test_size: float):
        x, y = data.get_training_data()
        model = MLPClassifier(hidden_layer_sizes=(64, 32), activation='relu', 
                              solver='adam', max_iter=1000, random_state=42)
        water_model.__init__(self, model, x, y, {}, test_size)
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(
            self.x, self.y, test_size=self.test_size)

    def predict(self):
        scaler = StandardScaler()
        self.x_train = scaler.fit_transform(self.x_train)
        self.x_test = scaler.transform(self.x_test)

        self.model.fit(self.x_train, self.y_train.ravel())
        self.y_predicted = self.model.predict(self.x_test)
        self._calculate_scores()

    def _calculate_scores(self):
        self.scores["Accuracy"] = accuracy_score(self.y_test, self.y_predicted)
        self.scores["Precision"] = precision_score(self.y_test, self.y_predicted)
        self.scores["Recall"] = recall_score(self.y_test, self.y_predicted)
        self.scores["F1_precision"] = f1_score(self.y_test, self.y_predicted)


class water_naive_bayes(water_model):
    """ Implementazione Naive Bayes (Cap. 9-10) """
    def __init__(self, data: water_data, test_size: float):
        x, y = data.get_training_data()
        water_model.__init__(self, GaussianNB(), x, y, {}, test_size)
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(
            self.x, self.y, test_size=self.test_size)

    def predict(self):
        # Naive Bayes non richiede necessariamente scaling, ma per coerenza col resto del progetto
        # e se ci sono feature con scale molto diverse, non fa male.
        self.model.fit(self.x_train, self.y_train.ravel())
        self.y_predicted = self.model.predict(self.x_test)
        self._calculate_scores()

    def _calculate_scores(self):
        self.scores["Accuracy"] = accuracy_score(self.y_test, self.y_predicted)
        self.scores["Precision"] = precision_score(self.y_test, self.y_predicted)
        self.scores["Recall"] = recall_score(self.y_test, self.y_predicted)
        self.scores["F1_precision"] = f1_score(self.y_test, self.y_predicted)