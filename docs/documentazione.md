# Titolo Progetto: Water Quality Expert System

### Sottotitolo: Un approccio ibrido (ML + Rule-Based) per l'analisi della potabilità dell'acqua

---

## 1. Introduzione e Dominio Applicativo

* **Di cosa parlare:** Inizia spiegando che l'accesso all'acqua potabile è una sfida globale. Invece di parlare di diabete, spiega che il progetto mira a automatizzare la classificazione della qualità dell'acqua.


* **Obiettivo:** Realizzare un sistema di supporto alle decisioni (DSS) che aiuti i tecnici di laboratorio a identificare rapidamente campioni contaminati.
* **Riferimento normativo:** Cita l'Organizzazione Mondiale della Sanità (WHO) come fonte delle soglie di sicurezza (pH, Torbidità) usate nel sistema.

## 2. Dataset e Pre-processing (Machine Learning)

* **Descrizione Dataset:**
* Fonte: Kaggle (Water Quality Dataset).
* Dimensioni: ~3200 istanze (righe), 9 feature (colonne).
* Descrivi le feature principali: pH, Hardness (Durezza), Solids (TDS), Chloramines, Turbidity.
* Target: `Potability` (0 = Non potabile, 1 = Potabile).


* **Pre-processing (Importante):**
* Scrivi di aver gestito i valori mancanti (`NaN`) eliminando le righe incomplete (o sostituendoli con la media, come fatto nel codice `water_data.py`).
* Menziona la normalizzazione dei dati (`StandardScaler`) usata prima dell'addestramento per rendere confrontabili parametri con scale diverse (es. pH 0-14 vs Solidi 10.000+).



## 3. Modelli di Classificazione e Valutazione

*Qui inserisci i grafici generati da `main_models.py`.*

* **Algoritmi Scelti:**
1. 
**Logistic Regression:** Scelta come baseline per la sua interpretabilità statistica.


2. 
**Decision Tree:** Scelto per la capacità di simulare regole decisionali umane (IF-THEN).


3. 
**K-Nearest Neighbors (KNN):** Scelto per analizzare la similarità tra campioni d'acqua vicini nello spazio vettoriale.




* **Metodologia di Valutazione (Cruciale per il Prof):**
* Non limitarti a una singola esecuzione. Scrivi: *"Per garantire la robustezza dei risultati, come richiesto dalle linee guida, i modelli sono stati valutati su più run, calcolando media e deviazione standard delle metriche"*.


* **Risultati:**
* Inserisci le **Matrici di Confusione** (i quadrati colorati).
* Commenta quale modello ha performato meglio (probabilmente Random Forest o Decision Tree sul dataset dell'acqua).



## 4. Knowledge Base e Ontologia

* **L'Ontologia (`water_quality.owl`):**
* Spiega di aver modellato il dominio usando **Protégé**.
* **Struttura:**
* Classi: `WaterSample`, `Parameter`.
* Proprietà: `hasPH`, `hasTurbidity`, `isPotable`.


* **Utilizzo:** L'ontologia funge da "dizionario semantico" che il sistema interroga per fornire descrizioni agli utenti (tramite la libreria `Owlready2`).
* *Suggerimento:* Inserisci uno screenshot del grafo di Protégé (o usa quello che ti genero qui sotto per ispirazione).



## 5. Il Sistema Esperto (Rule-Based Reasoning)

* **Tecnologia:** Libreria `experta` (motore inferenziale basato su algoritmo Rete/CLIPS).
* **Logica dei Fatti:**
* Spiega che ogni campione d'acqua viene trasformato in un insieme di `Fact` (es. `Fact(ph=4.5)`).


* **Le Regole (Knowledge Engineering):**
* Descrivi come hai tradotto le direttive WHO in regole Python.
* *Esempio da scrivere:*
> "Abbiamo implementato una regola di sicurezza critica: SE il pH è < 6.5 (Acido) O > 8.5 (Basico), ALLORA il sistema sovrascrive la predizione del Machine Learning e segnala 'NON POTABILE', garantendo la sicurezza umana."




* **Interazione:** Descrivi il menu interattivo dove l'utente inserisce i dati e riceve il responso colorato.

## 6. Constraint Satisfaction Problem (CSP)

* **Il Problema:** Gestione dei turni dei laboratori di analisi.
* **Variabili:** I giorni della settimana e le fasce orarie.
* **Vincoli (Constraints):**
* Esempio: "Il laboratorio chimico è aperto solo Lunedì mattina e Giovedì pomeriggio".
* Spiega che il solver (`python-constraint`) trova tutte le combinazioni di orari validi per prenotare un'analisi approfondita in caso di acqua contaminata.



## 7. Conclusioni e Sviluppi Futuri

* Riassumi dicendo che il sistema combina l'efficienza del Machine Learning (analisi rapida su grandi dati) con l'affidabilità del Sistema Esperto (regole di sicurezza rigide).
* **Sviluppi futuri:** Integrazione con sensori IoT per la lettura automatica del pH in tempo reale.

---

### Consigli pratici per la scrittura

1. **Copia-Incolla Intelligente:** Prendi i paragrafi teorici della vecchia relazione (es. "3.1 Albero di decisione", "3.3 K-nearest neighbor"). Quelli sono teoria generale, vanno bene anche per l'acqua! Cambia solo se ci sono riferimenti specifici al "paziente" o al "sangue".

2. **Screenshot Nuovi:** Non usare le vecchie immagini del diabete. Esegui il tuo `main_models.py`, fai gli screenshot dei grafici blu/arancioni che escono e incollali al posto di quelli vecchi.

3. **Formattazione:** Usa grassetti per le parole chiave (**Accuracy**, **Knowledge Base**, **WHO**). Il professore scorre velocemente, le parole chiave devono saltare all'occhio.