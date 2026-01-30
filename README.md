# 💧 Water Quality Assessment System
### Sistema Ibrido per l'Analisi della Potabilità dell'Acqua

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Experta](https://img.shields.io/badge/Experta-Rule--Based-green?style=for-the-badge)
![Ontology](https://img.shields.io/badge/OWL-Protégé-red?style=for-the-badge)

**Corso:** Ingegneria della Conoscenza (ICon) - Università degli Studi di Bari Aldo Moro  
**Anno Accademico:** 2025/2026

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

Questo progetto implementa un **Sistema di Supporto alle Decisioni (DSS)** per la valutazione della qualità dell'acqua. L'architettura è ibrida e combina più approcci dell'Intelligenza Artificiale:

1.  **Approccio Data-Driven (Machine Learning):** Analisi statistica e predittiva su dataset storici per classificare rapidamente la potabilità.
2.  **Approccio Knowledge-Based (Sistema Esperto):** Ragionamento simbolico basato su regole esplicite (standard WHO) e ontologie per validare i risultati e gestire casi critici (es. contaminazione chimica).
3.  **Ontologia OWL**  Modella concetti del dominio (campioni e condizioni di rischio) usata per recuperare descrizioni dei parametri, e per eseguire un controllo semantico con reasoner su classi definite
4.  **CSP Scheduler (Constraint Satisfaction Problem)** In caso di problemi rilevati, il sistema può attivare un CSP per suggerire una assegnazione operativa **(staff, day, shift)** coerente con il tipo di issue, e per l'ottimizzazione della pianificazione dei turni nei laboratori di analisi.
5.  **Interfaccia Streamlit + Modello Bayesiano**  È presente una UI Streamlit e un modulo bayesiano per stimare probabilità/indicatori di rischio

---

## 📂 Struttura del Progetto

```text
├── docs/
│   └── documentazione.md
├── images/
│   ├── architettura_sistema.png
│   └── ...
├── ontology/
│   ├── water_quality.owl
│   └── ontology_builder.py
├── src/
│   ├── bayesian_model.py
│   ├── data_loader.py
│   ├── expert_system.py
│   ├── ml_models.py
│   ├── ml_evaluation.py
│   ├── ontology_manager.py
│   └── scheduler.py
├── app.py
├── main_ml.py
├── main_expert.py
...
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
* *Neural Network (MLP)*: modello non-lineare più flessibile.
* *Gaussian Naive Bayes*: modello probabilistico generativo.

* **Metriche:** Accuracy (utilizzata come metrica principale, mediata in cross-validation); altre metriche (Precision, Recall, F1-Score) sono calcolate a supporto.


### 2. Modulo Sistema Esperto (Rule-Based)

Un agente intelligente implementato con la libreria `experta` (basata sull'algoritmo Rete) che applica regole di dominio.

* **Knowledge Base:** Ontologia OWL gestita tramite `Owlready2` che definisce la semantica del dominio (es. `WaterSample` e classi di anomalia come `AcidicWater`, `HighSulfateWater`).
* **Regole WHO**: Applicazione di vincoli di sicurezza (es. pH, Solfati) le cui soglie sono caricate dinamicamente dall'Ontologia all'avvio (`Single Source of Truth`), garantendo flessibilità e manutenibilità senza modificare il codice sorgente.
* **CSP Scheduler:** Utilizzo di `python-constraint` per allocare le analisi di laboratorio rispettando vincoli di orario e disponibilità dei tecnici.

### 3. Modulo Ontologia OWL (Semantica + Reasoner opzionale)

Strato semantico che modella formalmente il dominio (campione d’acqua, parametri e classi di rischio) e abilita inferenza automatica quando disponibile un reasoner.

* **Classi/concetti principali:** `WaterSample`, `AcidicWater`, `HighSulfateWater`, `TurbidWater`, `UnsafeWater`, `CorrosiveWater`.
* **Data Properties:** `has_ph_value`, `has_sulfate_value`, `has_turbidity_value`.
* **Integrazione nel codice:** `src/ontology_manager.py`
  * agisce come base di configurazione per il KBS, fornendo i valori limite per i parametri di rischio tramite un parsing robusto e ricorsivo. (es. `get_parameter_description`);
  * prova ad attivare il reasoner con `sync_reasoner_pellet()` (con **fallback** se non disponibile);
  * esegue un controllo semantico **opzionale** focalizzato su `CorrosiveWater` (solo se il reasoner è attivo).

### 4. Modulo CSP Scheduler (Pianificazione a Vincoli)

Modulo operativo che traduce la diagnosi simbolica in una decisione di pianificazione, risolvendo un problema di assegnazione come CSP.

* **Output:** una terna **(staff, day, shift)** in base a `issue_type` (`chemical`, `physical`, `critical`).
* **Logica:**
  * filtra a priori il dominio dello **staff** in base alla tipologia di problema;
  * applica vincoli di disponibilità/turnazione e compatibilità;
  * restituisce una soluzione valida al KBS, che la presenta come suggerimento operativo.

### 5. Interfaccia Streamlit + Modello Bayesiano

Componente applicativa per l’utilizzo interattivo del sistema e per stimare indicatori probabilistici tramite una rete bayesiana.

* **UI:** `app.py` (avvio dell’interfaccia Streamlit).
* **Bayesian Model:** `src/bayesian_model.py`
  * implementa una **rete bayesiana** (libreria `pgmpy`);
  * stima probabilità/indicatori coerentemente con la struttura e le query definite nel codice.


---

## 🚀 Guida all'Installazione

1. **Prerequisiti:** Python 3.10 o superiore.
2. **Clonare la repository** (o scaricare lo zip):
```bash
git clone https://github.com/Carmine365/Progetto_ICon_2026.git
cd Progetto_ICon_2026


```


3. **Installare le dipendenze:**
Si consiglia di creare un ambiente virtuale pulito.
```bash
pip install -r requirements.txt

```



---

## 💻 Guida all'Utilizzo

Il software offre tre modalità di esecuzione distinte.

### Modalità 1: Analisi Dati & Training (ML)

Esegue il training dei modelli, calcola le matrici di confusione e genera i grafici comparativi delle performance.

```bash
python main_ml.py

```

### Modalità 2: Agente Esperto Interattivo

Avvia l’interfaccia testuale del sistema esperto per l’inserimento di osservazioni e parametri di un campione d’acqua e la relativa analisi rule-based.

```bash
python main_expert.py

```

### Modalità 3: Web App Streamlit (UI + Bayesian Model)

Avvia un’interfaccia web (Streamlit) per usare il progetto in modo interattivo, senza passare dalla CLI.
Questa modalità è pensata come “front-end”  per inserire o selezionare parametri di un campione d’acqua, mostrando una valutazione/indicatori basati sul **modello bayesiano**

```bash
streamlit run app.py

```

---

*Powered by Python, Scikit-Learn, Experta & Owlready2.*
