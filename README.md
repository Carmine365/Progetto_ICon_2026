# 💧 Water Quality Assessment System
### Sistema Ibrido per l'Analisi della Potabilità dell'Acqua

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Experta](https://img.shields.io/badge/Experta-Rule--Based-green?style=for-the-badge)
![Ontology](https://img.shields.io/badge/OWL-Protégé-red?style=for-the-badge)

**Corso:** Ingegneria della Conoscenza (ICon) - Università degli Studi di Bari Aldo Moro  
**Anno Accademico:** 2022/2023

---

## 👥 Autori

Progetto realizzato per l'esame di Ingegneria della Conoscenza.

* **Carmine Giove**
* Matricola: 797656
* Email: c.giove10@studenti.uniba.it


* **Claudio Gualberti**
* Matricola: 801963
* Email: c.gualberti@studenti.uniba.it


---

## 📋 Descrizione del Progetto

Questo progetto implementa un **Sistema di Supporto alle Decisioni (DSS)** per la valutazione della qualità dell'acqua. L'architettura è ibrida e combina due approcci dell'Intelligenza Artificiale:

1.  **Approccio Data-Driven (Machine Learning):** Analisi statistica e predittiva su dataset storici per classificare rapidamente la potabilità.
2.  **Approccio Knowledge-Based (Sistema Esperto):** Ragionamento simbolico basato su regole esplicite (standard WHO) e ontologie per validare i risultati e gestire casi critici (es. contaminazione chimica).

Il sistema include anche un modulo **CSP (Constraint Satisfaction Problem)** per l'ottimizzazione della pianificazione dei turni nei laboratori di analisi.

---

## 📂 Struttura del Progetto

```text
WATER_QUALITY_PROJECT/
│
├── data/                       # Dataset CSV
│   └── water_potability.csv
│
├── ontology/                   # Base di Conoscenza
│   └── water_quality.owl       # File OWL (Protégé)
│
├── src/                        # Codice Sorgente
│   ├── data_loader.py          # Pre-processing e caricamento dati
│   ├── expert_system.py        # Agente intelligente (Experta)
│   ├── ml_models.py            # Classificatori ML (LogReg, DT, KNN)
│   ├── ml_evaluation.py        # Metriche e grafici comparativi
│   ├── ontology_manager.py     # Interfaccia Python-OWL
│   └── scheduler.py            # Risolutore CSP per i laboratori
│
├── docs/                       # Documentazione
│   └── Relazione_Icon.pdf
│
├── main_ml.py                  # Entry point: Analisi Machine Learning
├── main_expert.py              # Entry point: Sistema Esperto Interattivo
├── requirements.txt            # Dipendenze
└── README.md                   # Questo file

```

---

## 🧠 Moduli e Tecnologie

### 1. Modulo Machine Learning

Addestramento di classificatori supervisionati per predire la variabile target `Potability`.

* **Dataset:** 3276 istanze con 9 feature (pH, Hardness, Solids, Chloramines, Sulfate, Conductivity, Organic_carbon, Trihalomethanes, Turbidity).
* **Algoritmi:**
* *Logistic Regression*: Baseline statistica.
* *Decision Tree*: Modello interpretabile a regole.
* *K-Nearest Neighbors (KNN)*: Classificazione basata su similarità.


* **Metriche:** Accuracy, Precision, Recall, F1-Score (mediate su multiple esecuzioni).

### 2. Modulo Sistema Esperto (Rule-Based)

Un agente intelligente implementato con la libreria `experta` (basata sull'algoritmo Rete) che applica regole di dominio.

* **Knowledge Base:** Ontologia OWL gestita tramite `Owlready2` che definisce la semantica dei parametri (es. `WaterSample`, `ChemicalParameter`).
* **Regole WHO:** Implementazione di soglie rigide di sicurezza (es. `IF pH < 6.5 THEN Non-Potabile`).
* **CSP Scheduler:** Utilizzo di `python-constraint` per allocare le analisi di laboratorio rispettando vincoli di orario e disponibilità dei tecnici.

---

## 🚀 Guida all'Installazione

1. **Prerequisiti:** Python 3.10 o superiore.
2. **Clonare la repository** (o scaricare lo zip):
```bash
git clone https://github.com/Carmine365/Progetto_ICon_2026.git
cd WATER_QUALITY_PROJECT

```


3. **Installare le dipendenze:**
Si consiglia di creare un ambiente virtuale pulito.
```bash
pip install -r requirements.txt

```



---

## 💻 Guida all'Utilizzo

Il software offre due modalità di esecuzione distinte.

### Modalità 1: Analisi Dati & Training (ML)

Esegue il training dei modelli, calcola le matrici di confusione e genera i grafici comparativi delle performance.

```bash
python main_ml.py

```

### Modalità 2: Agente Esperto Interattivo

Avvia l'interfaccia testuale per interrogare l'ontologia o sottoporre un nuovo campione d'acqua all'analisi dell'esperto artificiale.

```bash
python main_expert.py

```

*Seguire le istruzioni a schermo per navigare nel menu.*

---


*Powered by Python, Scikit-Learn, Experta & Owlready2.*

```

```
