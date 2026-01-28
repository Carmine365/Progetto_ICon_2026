from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score,
                             confusion_matrix, f1_score, precision_score,
                             recall_score, roc_curve, auc)
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn import tree
import matplotlib.pyplot as plt
from typing import Final
import numpy as np

# Import relativo per il package src
from .data_loader import waterData 

class waterModel:

    def __init__(self, model, x, y, scores_dict: dict, test_size: float):
        default_test_size: Final = 0.2

        if not (0 < test_size < 1):
            test_size = default_test_size

        self.model = model
        self.x = x
        self.y = y
        self.scores = scores_dict
        self.test_size = test_size
        self.target = "Potability"
        
        # Variabili per i risultati CV
        self.cv_means = {}
        self.cv_stds = {}

        self.x_train = None
        self.x_test = None
        self.y_train = None
        self.y_test = None
        self.y_predicted = None

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    # --- METODI RIPRISTINATI PER COMPATIBILITÀ CON main_ml.py ---
    def get_metric(self, score_label: str):
        """Restituisce il valore di una metrica specifica dal dizionario scores"""
        return self.scores.get(score_label)

    def print_metrics(self):
        """Stampa a video le metriche calcolate nel singolo run"""
        print(f"       -> [Test Set] Accuracy: {self.scores.get('Accuracy', 0):.4f} | "
              f"Precision: {self.scores.get('Precision', 0):.4f} | "
              f"Recall: {self.scores.get('Recall', 0):.4f} | "
              f"F1: {self.scores.get('F1_precision', 0):.4f}")

    def get_roc_curve(self):
        """Genera e mostra la curva ROC se il modello supporta le probabilità"""
        if hasattr(self.model, "predict_proba") and self.x_test is not None and self.y_test is not None:
            try:
                # Calcola le probabilità della classe positiva (1)
                y_probs = self.model.predict_proba(self.x_test)[:, 1]
                fpr, tpr, _ = roc_curve(self.y_test, y_probs)
                roc_auc = auc(fpr, tpr)
                
                plt.figure(figsize=(8, 6))
                plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
                plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
                plt.xlim([0.0, 1.0])
                plt.ylim([0.0, 1.05])
                plt.xlabel('False Positive Rate')
                plt.ylabel('True Positive Rate')
                plt.title(f'ROC Curve - {self.__class__.__name__}')
                plt.legend(loc="lower right")
                plt.grid(alpha=0.3)
                plt.show()
            except Exception as e:
                print(f"       [Warning] Impossibile generare ROC: {e}")
        else:
            print(f"       [Info] Il modello {self.__class__.__name__} non supporta la curva ROC (manca predict_proba).")
    # ------------------------------------------------------------

    def get_confusion_matrix(self):
        if self.y_test is not None and self.y_predicted is not None:
            cm = confusion_matrix(self.y_test, self.y_predicted)
            disp = ConfusionMatrixDisplay(confusion_matrix=cm)
            disp.plot(cmap="Blues")
            plt.title(f'Confusion Matrix - {self.__class__.__name__}')
            plt.show()

    def evaluate_with_cross_validation(self, folds=10):
        """
        Esegue la Cross-Validation calcolando TUTTE le metriche.
        Restituisce tuple (media_accuracy, std_accuracy) per compatibilità con main_ml.py.
        """
        scoring = ['accuracy', 'precision', 'recall', 'f1']
        
        # Eseguiamo la CV
        scores = cross_validate(self.model, self.x, self.y.ravel(), cv=folds, scoring=scoring)
        
        # Salviamo Medie e Deviazioni Standard
        self.cv_means = {
            'Accuracy': scores['test_accuracy'].mean(),
            'Precision': scores['test_precision'].mean(),
            'Recall': scores['test_recall'].mean(),
            'F1': scores['test_f1'].mean()
        }
        
        self.cv_stds = {
            'Accuracy': scores['test_accuracy'].std(),
            'Precision': scores['test_precision'].std(),
            'Recall': scores['test_recall'].std(),
            'F1': scores['test_f1'].std()
        }
        
        # Restituiamo Accuracy Mean e Std come si aspetta il tuo main_ml.py
        return self.cv_means['Accuracy'], self.cv_stds['Accuracy']

    # --- Metodi di supporto per il train/test split singolo ---
    def _single_split_fit(self):
        scaler = StandardScaler()
        if self.x_train is None or self.x_test is None or self.y_train is None:
            raise ValueError("x_train, x_test, and y_train must not be None before fitting.")
        self.x_train = scaler.fit_transform(self.x_train)
        self.x_test = scaler.transform(self.x_test)
        self.model.fit(self.x_train, self.y_train.ravel())
        self.y_predicted = self.model.predict(self.x_test)
        self._calculate_scores()

    def _calculate_scores(self):
        if self.y_test is not None and self.y_predicted is not None:
            self.scores["Accuracy"] = accuracy_score(self.y_test, self.y_predicted)
            self.scores["Precision"] = precision_score(self.y_test, self.y_predicted, zero_division=0)
            self.scores["Recall"] = recall_score(self.y_test, self.y_predicted, zero_division=0)
            self.scores["F1_precision"] = f1_score(self.y_test, self.y_predicted, zero_division=0)
        else:
            self.scores["Accuracy"] = 0.0
            self.scores["Precision"] = 0.0
            self.scores["Recall"] = 0.0
            self.scores["F1_precision"] = 0.0

# --- SOTTOCLASSI ---

class waterLogReg(waterModel):
    def __init__(self, data: waterData, test_size: float):
        x, y = data.get_training_data()
        super().__init__(LogisticRegression(max_iter=1000), x, y, {}, test_size)
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(self.x, self.y, test_size=self.test_size)

    def predict(self):
        self._single_split_fit()

class waterDecTree(waterModel):
    def __init__(self, data: waterData, test_size: float):
        x, y = data.get_training_data()
        super().__init__(tree.DecisionTreeClassifier(max_depth=5), x, y, {}, test_size)
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(self.x, self.y, test_size=self.test_size)

    def predict(self):
        # I tree non necessitano di scaling obbligatorio
        self.model.fit(self.x_train, self.y_train.ravel())
        self.y_predicted = self.model.predict(self.x_test)
        self._calculate_scores()

class waterKnn(waterModel):
    def __init__(self, data: waterData, test_size: float, neighbors: int):
        x, y = data.get_training_data()
        super().__init__(KNeighborsClassifier(n_neighbors=neighbors), x, y, {}, test_size)
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(self.x, self.y, test_size=self.test_size)

    def predict(self):
        self._single_split_fit()

class waterNeuralNetwork(waterModel):
    def __init__(self, data: waterData, test_size: float):
        x, y = data.get_training_data()
        super().__init__(MLPClassifier(hidden_layer_sizes=(64,32), max_iter=1000), x, y, {}, test_size)
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(self.x, self.y, test_size=self.test_size)

    def predict(self):
        self._single_split_fit()

class waterNaiveBayes(waterModel):
    def __init__(self, data: waterData, test_size: float):
        x, y = data.get_training_data()
        super().__init__(GaussianNB(), x, y, {}, test_size)
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(self.x, self.y, test_size=self.test_size)

    def predict(self):
        self.model.fit(self.x_train, self.y_train.ravel())
        self.y_predicted = self.model.predict(self.x_test)
        self._calculate_scores()