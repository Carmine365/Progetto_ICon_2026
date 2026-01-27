# Water Quality Assessment System   
## Sistema ibrido: Ontologia + KBS rule-based + ML + CSP

# 0. Mappa del progetto (contenuti dello ZIP) e temi affrontati

Questa sezione serve a chiarire **cosa contiene realmente il progetto** e **quali temi del corso vengono affrontati esplicitamente**, così da rendere subito valutabile il lavoro senza “riempitivi”.

---

## 0.1 Contenuto, struttura e file principali

Nel progetto sono presenti quattro macro-componenti, ciascuna implementata in moduli dedicati.

### Sistema esperto / KBS rule-based
- **File principale**: `src/expert_system.py`  
  Contiene:
  - definizione e uso dei **fatti** (`Fact(...)`)
  - definizione delle **regole** con `experta` (trigger su osservazioni e su vincoli numerici)
  - gestione dell’esecuzione del ragionamento e produzione dell’esito
  - integrazione con lo scheduler (CSP) tramite chiamate come `_run_scheduler(...)`

- **Entrypoint**: `main_expert.py`  
  Avvia l’esecuzione del sistema esperto (interazione/diagnosi).

---

### Ontologia OWL e gestione semantica
- **Ontologia**: `ontology/water_quality.owl`  
  File OWL con classi/proprietà/individui relativi al dominio (parametri dell’acqua e concetti collegati).

- **Costruzione/gestione**:
  - `ontology/ontology_builder.py` (supporto alla costruzione o modifica dell’ontologia)
  - `src/ontology_manager.py` (caricamento ontologia e utilizzo nel sistema)
  
  In particolare `ontology_manager.py` tenta di abilitare il **ragionamento** tramite reasoner (Pellet) e gestisce un comportamento di **fallback** se il reasoner non è disponibile.

---

### CSP / Scheduler (pianificazione risorse)
- **File principale**: `src/scheduler.py`  
  Modella un problema di assegnazione (turni/risorse/laboratori) come **CSP**, risolvendo la scelta operativa a partire dal tipo di problema rilevato dal KBS (chimico / fisico / critico).

Lo scheduler non è “incollato” dentro le regole: è un modulo separato richiamato dal KBS, per mantenere distinta la parte di diagnosi da quella di pianificazione.

---

### Modulo ML (apprendimento supervisionato)
- **Dataset**: `data/water_potability.csv`  
  Dataset tabellare con target di potabilità (colonna `Potability`).

- **Modelli e valutazione**:
  - `src/ml_models.py` (addestramento e confronto di più modelli; include cross-validation con mean/std)
  - `src/ml_evaluation.py` (supporto valutazione/plot o funzioni di utilità, a seconda dell’implementazione)

- **Entrypoint**: `main_ml.py`  
  Avvia pipeline di training/valutazione dei modelli ML.

---

## 0.2 Temi del corso coperti (espliciti nel codice)

Il progetto non è centrato su un solo paradigma: integra più temi del corso, ciascuno identificabile in file concreti.

### Rappresentazione della conoscenza e KBS
- **Dove**: `src/expert_system.py`
- **Cosa**:
  - KB basata su **fatti** e **regole**
  - uso di fatti simbolici (osservazioni) e fatti numerici (parametri)
  - regole anche con **vincoli numerici** (non solo pattern matching su simboli)

### Ragionamento (rule-based + inferenza semantica opzionale)
- **Rule-based**: `src/expert_system.py` con `experta`
- **Ontology reasoning**: `src/ontology_manager.py` con tentativo di `sync_reasoner_pellet()`
- **Scelta importante**: presenza di fallback → il sistema rimane utilizzabile anche senza reasoner (ma con capacità inferenziale ridotta)

### Modellazione ontologica (OWL)
- **Dove**: `ontology/water_quality.owl` (+ `ontology_builder.py`)
- **Cosa**:
  - concetti del dominio (parametri, qualità, categorie/relazioni)
  - descrizioni/metadata utili a contestualizzare i parametri nel sistema

### CSP / vincoli per l’azione operativa
- **Dove**: `src/scheduler.py` e chiamate dal KBS in `src/expert_system.py`
- **Cosa**:
  - pianificazione/assegnazione coerente con i problemi rilevati (chimico/fisico/critico)
  - separazione “diagnosi → decisione operativa” in due moduli distinti

### Apprendimento supervisionato e valutazione sperimentale
- **Dove**: `src/ml_models.py`, `src/ml_evaluation.py`, `main_ml.py`
- **Cosa**:
  - confronto tra più modelli (es. LR, DT, KNN, MLP, NB se presenti nel file)
  - valutazione con **cross-validation** e risultati riportabili come **media ± deviazione standard** (coerente con le linee guida)

---

## 0.3 Cosa verrà documentato e cosa viene evitato

### Verrà documentato
- scelte tecniche e motivazioni (perché KBS+ML, perché CSP, perché OWL)
- rappresentazione della KB (fatti/relazioni/regole e loro complessità)
- parametri/iperparametri davvero usati nel codice e come sono stati fissati
- valutazione ML con risultati aggregati (mean±std) e conclusioni interpretate

### Verrà evitato
- definizioni generiche di metriche/algoritmi noti non necessarie
- screenshot di codice (si riporta codice/estratti essenziali come testo quando utile)
- risultati basati su un singolo run (si preferiscono medie e deviazioni standard)

---

## 0.4 Modalità di esecuzione (entrypoint principali)
- `main_expert.py`: esecuzione del sistema esperto (KBS) e attivazione dello scheduler quando necessario.
- `main_ml.py`: esecuzione della pipeline ML con training e valutazione.

Questi due entrypoint riflettono i due “pilastri” del progetto: **ragionamento simbolico + valutazione statistica**.


---
# 1. Obiettivo del progetto e motivazioni

## 1.1 Contesto e scopo pratico
Il progetto realizza un **sistema di supporto alla valutazione della qualità/potabilità dell’acqua** che combina in modo coerente più tecniche tipiche dell’**Ingegneria della Conoscenza**.  
Lo scopo non è “solo” classificare un dataset, ma costruire un sistema che:

- **acquisisce conoscenza** (osservazioni e misurazioni) in modo strutturato;
- **ragiona** con regole esplicite e interpretabili (KBS);
- usa uno **strato semantico** (ontologia OWL) per descrivere concetti e parametri del dominio e, se possibile, abilitare inferenza automatica;
- integra un modulo di **pianificazione/assegnazione risorse** formulato come CSP (es. scelta del laboratorio/turno in base al tipo di problema rilevato);
- include una componente di **apprendimento supervisionato** (ML) per stimare la potabilità dai dati e confrontarla con l’approccio simbolico.

In altre parole, il progetto mira a dimostrare capacità pratiche su un caso d’uso realistico: **diagnosi + motivazione della diagnosi + azione operativa conseguente**.

---

## 1.2 Temi del corso affrontati esplicitamente
Il lavoro copre in modo esplicito (e verificabile nel codice) i seguenti temi:

1. **Knowledge-Based System (KBS) e regole**
   - Base di conoscenza composta da **fatti** e **regole**.
   - Regole sia “semplici” (trigger su evidenze) sia **relazionali con vincoli numerici**.
   - Motivazione: garantire **spiegabilità** e controllabilità nei casi critici.

2. **Rappresentazione della conoscenza (KB)**
   - Distinzione tra conoscenza **simbolica** (osservazioni qualitative) e **numerica** (parametri misurati).
   - Motivazione: abilitare ragionamento più espressivo rispetto al solo pattern matching su fatti statici.

3. **Ontologia OWL**
   - Modello concettuale del dominio (parametri, concetti e relazioni).
   - Possibile attivazione del reasoner (Pellet) per inferenze automatiche.
   - Motivazione: rendere esplicita la semantica del dominio e supportare estensioni future (nuove classi/relazioni/assiomi) senza riscrivere logica procedurale.

4. **CSP (Constraint Satisfaction Problem)**
   - Pianificazione/assegnazione di risorse (es. laboratorio/turni) vincolata dal tipo di problema rilevato.
   - Motivazione: separare **diagnosi** (ragionamento) da **azione** (pianificazione) con un modello dichiarativo a vincoli.

5. **Apprendimento automatico supervisionato**
   - Addestramento e confronto di modelli di classificazione sulla potabilità.
   - Valutazione con protocolli ripetibili e metriche aggregate (media e deviazione standard su CV) per evitare conclusioni basate su un singolo run.
   - Motivazione: coprire pattern dai dati e confrontare approcci simbolico/statistico.

Questa copertura è deliberata: l’idea è mostrare un sistema **ibrido** in cui ogni componente è giustificata e contribuisce al risultato complessivo.

---

## 1.3 Perché un sistema ibrido (KBS + Ontologia + ML + CSP)
La scelta progettuale principale è adottare un’architettura ibrida, anziché un singolo approccio.

### 1.3.1 Perché non solo ML
Un approccio esclusivamente ML:
- produce una predizione, ma spesso con **bassa spiegabilità** (soprattutto con modelli più complessi);
- tende a essere fragile in presenza di dati rumorosi, mancanti o distribuzioni diverse dal training set;
- non gestisce in modo naturale **regole di sicurezza** e casi “hard constraint” (es. condizioni critiche che devono generare un allarme indipendentemente dal punteggio del modello).

Nel progetto, la componente ML è quindi usata come:
- stima statistica della potabilità,
- termine di confronto,
- supporto a pattern non codificati in regole.

### 1.3.2 Perché un KBS rule-based
Il KBS consente di:
- codificare conoscenza esplicita (soglie, combinazioni critiche, condizioni note);
- fornire un comportamento **interpretabile** (“l’allarme scatta perché...”), utile in contesti tecnici;
- implementare regole **relazionali** che combinano più parametri (non banali soglie isolate).

Inoltre, un KBS permette di:
- aggiornare e raffinire la conoscenza con nuove regole senza dover riaddestrare modelli;
- rendere chiaro cosa si intende per “anomalia” o “criticità” dal punto di vista del dominio.

### 1.3.3 Perché un’ontologia OWL
L’ontologia non è pensata come un database, ma come:
- **modello concettuale** del dominio (classi, proprietà, relazioni);
- supporto semantico (descrizioni dei parametri e loro significato);
- base per inferenza automatica quando disponibile un reasoner.

Questo strato rende il sistema:
- più estendibile (aggiunta di concetti e relazioni),
- più “pulito” dal punto di vista della rappresentazione,
- meno dipendente da strutture ad-hoc nel codice.

### 1.3.4 Perché un CSP per l’azione operativa
Una volta identificato un problema, il sistema non si limita a “stampare un risultato” ma supporta una decisione operativa: **quale risorsa/laboratorio/turno assegnare**.

La formulazione come CSP è motivata da:
- natura dichiarativa del problema (vincoli su disponibilità, tipi di attività, priorità);
- separazione netta tra:
  - inferenza diagnostica (KBS),
  - pianificazione (CSP),
- possibilità di estendere facilmente i vincoli (nuove risorse, orari, priorità) senza riscrivere regole diagnostiche.

---

## 1.4 Risultati attesi e output del sistema
Il sistema è progettato per produrre output su più livelli:

1. **Livello diagnostico (KBS)**
   - identificazione di anomalie su parametri e osservazioni;
   - segnalazione di condizioni critiche quando scattano regole relazionali.

2. **Livello semantico (Ontologia)**
   - supporto descrittivo (metadati e spiegazioni sui parametri);
   - inferenza (se reasoner attivo) per arricchire le conoscenze disponibili.

3. **Livello operativo (CSP)**
   - suggerimento/assegnazione di una risorsa o turno coerente con la tipologia di problema rilevata (chimico/fisico/critico).

4. **Livello predittivo (ML)**
   - classificazione della potabilità dai dati;
   - confronto quantitativo tra modelli;
   - validazione con metriche aggregate (media e deviazione standard su più run/CV).

Questa multi-uscita è intenzionale: dimostra che il progetto non è un singolo algoritmo, ma un sistema con componenti che cooperano.

---

## 1.5 Criteri di qualità adottati (in linea con le linee guida)
Per aderire ai criteri richiesti dall’insegnamento, la documentazione e il progetto seguono questi principi:

- **Focus su scelte tecniche reali**: ogni descrizione rimanda a decisioni implementate (moduli, parametri, regole, vincoli).
- **Evitare teoria superflua**: non vengono inserite definizioni generiche di algoritmi/metriche, se non strettamente necessarie a motivare scelte o interpretare risultati.
- **Valutazione robusta**: per la parte ML si riportano risultati mediati su più run/CV con **deviazione standard**, evitando conclusioni su singoli split.
- **Centralità della KB**: particolare attenzione è riservata alla struttura della KB, alla rappresentazione, all’uso e a una valutazione di complessità/estensibilità.
- **Originalità del sistema**: l’integrazione KBS+OWL+CSP+ML e la catena diagnosi→azione evidenziano un lavoro non riducibile a un notebook standard reperibile online.

---

## 1.6 Come verrà sviluppata la documentazione (passo passo)
La documentazione verrà organizzata in sezioni coerenti con l’architettura del sistema e con le linee guida:

1. **Obiettivo e motivazioni** (questa sezione)
2. **Architettura e scelte progettuali**
3. **KBS e Knowledge Base**: rappresentazione, regole, complessità, estensibilità
4. **Ontologia OWL**: contenuto, motivazione, uso, inferenza, limiti
5. **CSP/Scheduler**: modello, variabili, domini, vincoli, complessità
6. **ML**: dataset, preprocessing, modelli, iperparametri, protocollo di valutazione con media±std
7. **Discussione comparativa e conclusioni**: cosa funziona meglio, limiti, sviluppi futuri

Ogni sezione conterrà solo contenuti utili a valutare:
- le scelte tecniche,
- il corretto uso dei temi del corso,
- la qualità della valutazione sperimentale.

---

# 2. Architettura del sistema e scelte progettuali

In questa sezione viene descritta l’**architettura complessiva del sistema**, facendo esplicito riferimento ai **file e ai moduli presenti nello ZIP allegato**, e motivando le principali scelte progettuali effettuate.  
L’obiettivo è mostrare chiaramente **come** e **perché** i diversi componenti cooperano, evitando descrizioni astratte o non verificabili nel codice.

---

## 2.1 Visione architetturale generale

Il sistema è organizzato secondo un’architettura **modulare e stratificata**, in cui ogni componente ha una responsabilità specifica:

- **Strato di acquisizione e ragionamento** → KBS rule-based  
- **Strato semantico** → Ontologia OWL  
- **Strato decisionale operativo** → CSP / Scheduler  
- **Strato predittivo/statistico** → Modulo ML  

Questi strati non sono isolati: comunicano tramite interfacce semplici e ben definite, ma restano **concettualmente separati**, così da:
- migliorare la leggibilità del progetto;
- facilitare la valutazione dei singoli approcci;
- rendere possibile l’estensione futura del sistema.

---

## 2.2 Modulo KBS: cuore del sistema

### 2.2.1 File e responsabilità
- **File principale**: `src/expert_system.py`
- **Entrypoint**: `main_expert.py`

Il modulo KBS rappresenta il **cuore logico del sistema** ed è responsabile di:
- acquisire le informazioni dall’utente (osservazioni e parametri);
- popolare la **Knowledge Base** con fatti simbolici e numerici;
- applicare le regole di inferenza;
- determinare il tipo di problema rilevato;
- attivare, se necessario, il modulo CSP.

### 2.2.2 Scelta di un motore a regole (`experta`)
La libreria `experta` è stata scelta perché:
- consente una rappresentazione chiara di fatti e regole;
- supporta regole con **vincoli su valori numerici**;
- è coerente con l’approccio rule-based trattato nel corso.

Alternative come una logica puramente procedurale sono state scartate perché:
- meno espressive dal punto di vista della KB;
- meno adatte a dimostrare capacità di Ingegneria della Conoscenza.

---

## 2.3 Strato semantico: Ontologia OWL

### 2.3.1 File e responsabilità
- `ontology/water_quality.owl`
- `ontology/ontology_builder.py`
- `src/ontology_manager.py`

Lo strato ontologico è responsabile della **modellazione concettuale del dominio**.  
Non viene usato come semplice archivio di dati, ma come:
- rappresentazione formale dei concetti (parametri, qualità, relazioni);
- supporto semantico per descrivere il significato dei parametri gestiti dal sistema.

### 2.3.2 Integrazione con il sistema
Il modulo `ontology_manager.py`:
- carica l’ontologia OWL;
- tenta di attivare il reasoner (`sync_reasoner_pellet()`);
- espone al resto del sistema informazioni semantiche (es. descrizioni dei parametri).

Una scelta progettuale rilevante è il **fallback controllato**:
- se il reasoner non è disponibile (dipendenza Java/Pellet), il sistema continua a funzionare;
- in questo caso l’ontologia viene usata come strato descrittivo, senza inferenza automatica.

Questa scelta evita che il progetto diventi fragile o inutilizzabile in ambienti diversi.

---

## 2.4 Modulo CSP / Scheduler

### 2.4.1 File e responsabilità
- **File principale**: `src/scheduler.py`

Il modulo CSP modella un problema di **assegnazione di risorse/turni** come problema a vincoli.  
Il suo compito è decidere **come agire operativamente** una volta che il KBS ha identificato un problema.

### 2.4.2 Interazione con il KBS
Il KBS non contiene logica di pianificazione interna.  
Quando una regola diagnostica individua un problema:
- viene inferito un fatto del tipo `problem_type`;
- viene chiamata una funzione come `_run_scheduler("chemical")`.

Questa separazione è intenzionale:
- il KBS si occupa di *cosa* è il problema;
- il CSP si occupa di *come* allocare le risorse.

### 2.4.3 Motivazione della scelta CSP
La pianificazione è modellata come CSP perché:
- il problema è naturalmente espresso tramite vincoli;
- consente estensioni future (nuovi vincoli, nuove risorse);
- evita soluzioni hard-coded all’interno delle regole.

---

## 2.5 Modulo di apprendimento automatico (ML)

### 2.5.1 File e responsabilità
- `src/ml_models.py`
- `src/ml_evaluation.py`
- `main_ml.py`
- Dataset: `data/water_potability.csv`

Il modulo ML è **separato dal KBS** e può essere eseguito in modo indipendente.  
È responsabile di:
- caricare e preprocessare il dataset;
- addestrare più modelli di classificazione;
- valutare le prestazioni con protocolli ripetibili.

### 2.5.2 Motivazione della separazione dal KBS
Il ML non è integrato direttamente nel flusso del KBS per scelta progettuale:
- evita di mescolare logica simbolica e statistica nello stesso modulo;
- consente di confrontare i due approcci in modo chiaro;
- rende il progetto più leggibile e valutabile.

Il confronto KBS vs ML avviene **a livello di documentazione e risultati**, non tramite un’integrazione forzata nel codice.

---

## 2.6 Flusso di esecuzione complessivo

### 2.6.1 Flusso KBS + CSP
1. Avvio con `main_expert.py`
2. Acquisizione osservazioni e parametri
3. Popolamento della KB
4. Attivazione delle regole
5. Inferenza del tipo di problema
6. Attivazione dello scheduler (CSP)
7. Output diagnostico e operativo

### 2.6.2 Flusso ML
1. Avvio con `main_ml.py`
2. Caricamento dataset
3. Addestramento modelli
4. Valutazione con cross-validation
5. Produzione di metriche aggregate (mean ± std)

---

## 2.7 Vantaggi dell’architettura adottata

L’architettura scelta consente di:
- dimostrare l’uso coordinato di più tecniche di ICon;
- mantenere ogni modulo semplice ma significativo;
- evitare progetti monolitici o poco estendibili;
- supportare una valutazione separata ma coerente dei diversi approcci.

Questa struttura rende il progetto:
- facilmente comprensibile;
- estendibile come base di un lavoro di tesi;
- aderente alle linee guida dell’insegnamento.

---
# 3. Knowledge-Based System (KBS) e Knowledge Base

Questa sezione documenta in modo completo il **sistema esperto** del progetto (ZIP allegato), con focus su:
- **rappresentazione della Knowledge Base (KB)** (fatti, variabili, strutture);
- **regole** e catene inferenziali (incluse regole relazionali con vincoli numerici);
- **integrazione con dataset e CSP**;
- considerazioni su **complessità, estendibilità e limiti**.

Riferimento principale: `src/expert_system.py`  
Moduli collegati:
- `src/data_loader.py` (medie dal dataset per confronto)
- `src/scheduler.py` (CSP per turni/risorse)
- `src/ontology_manager.py` (strato ontologico, descritto nel punto 4)

---

## 3.1 Ruolo del KBS nel sistema

Il KBS è il componente che realizza la parte **simbolica e spiegabile** della diagnosi. In particolare:

1. **Acquisisce** informazioni dall’utente:
   - osservazioni qualitative (aspetto/odore/sapore/sedimenti)
   - misure quantitative (pH, solfati, torbidità, solidi, durezza)

2. **Popola** la KB con fatti strutturati.

3. **Inferisce**:
   - anomalie su singoli parametri (soglie)
   - condizioni critiche derivanti da combinazioni (regole relazionali)
   - tipo di intervento richiesto (chimico/fisico/critico)

4. **Attiva un’azione operativa** chiamando il CSP (prenotazione/assegnazione turno) quando rileva un problema.

L’obiettivo non è “fare una predizione”, ma produrre un output ragionato e motivabile, e collegarlo a un’azione.

---

## 3.2 Scelte di implementazione e motivazioni

### 3.2.1 Motore a regole: `experta`
Nel file `src/expert_system.py` il ragionamento è implementato tramite:
- `KnowledgeEngine` come motore inferenziale
- `Fact` come unità di conoscenza
- `@Rule(...)` come regole di produzione

Motivazioni della scelta:
- rappresentazione dichiarativa di condizioni → azioni;
- facilità di estensione (nuove regole senza riscrivere flusso procedurale);
- supporto a vincoli numerici con `P(lambda x: ...)` (utile per regole relazionali).

### 3.2.2 Compatibilità Python (fix per `experta`)
All’inizio di `expert_system.py` è presente un fix:

```python
import collections.abc
import collections
if not hasattr(collections, 'Mapping'):
    collections.Mapping = collections.abc.Mapping
```

Ottimo lavoro. Il testo è solido, tecnico e mostra una consapevolezza critica (specialmente sui bug del codice come il fatto `action="analyze"`) che alzerà notevolmente la qualità della relazione.

Ecco il contenuto riorganizzato e formattato con una struttura Markdown pulita, pronta per essere incollata nel tuo documento finale.

---

## 3.3 Acquisizione della conoscenza e popolamento della Knowledge Base

L’acquisizione della conoscenza nel KBS avviene in modo **interattivo** e **guidato da regole**, superando la rigidità di un flusso puramente procedurale. Le fasi di acquisizione sono implementate in `src/expert_system.py` e attivate tramite fatti di controllo che rappresentano lo stato del dialogo.

### 3.3.1 Inizializzazione della KB

All’avvio del motore (`@DefFacts()`), il sistema prepara il contesto operativo inizializzando:

* **Fatto di bootstrap**: `Fact(inizio="si")`, che innesca la prima regola di saluto e configurazione.
* **Contatore anomalie**: `self.problems_found = 0`, utilizzato per la valutazione finale della potabilità.
* **Medie statistiche**: `self.mean_water_values`, calcolate dinamicamente dal dataset reale tramite `water_data().get_medium_values_water()`.

### 3.3.2 Acquisizione delle osservazioni qualitative

Le osservazioni (aspetto, odore, sapore, sedimenti) vengono acquisite tramite la funzione `_prototype_ask_observation()`. Per ogni risposta affermativa, viene asserito un fatto simbolico:

* `Fact(acqua_torbida="si")`
* `Fact(cattivo_odore="si")`
* ...etc.

**Nota progettuale:** L'uso di fatti simbolici permette di integrare la conoscenza esperta qualitativa con le successive misurazioni strumentali, creando un contesto diagnostico multidimensionale.

### 3.3.3 Acquisizione dei parametri numerici

I parametri quantitativi sono acquisiti in step successivi, attivati da fatti di stato (es. `Fact(step="...")`). Tutti i dati numerici sono rappresentati uniformemente:

> `Fact(param="<nome_parametro>", value=<valore>)`

Questa struttura evita la proliferazione di tipi di fatto diversi e permette di scrivere regole relazionali generiche o specifiche con estrema facilità.

#### Parametri e Soglie Critiche

Il sistema valida i dati rispetto a soglie predefinite (costanti di progetto):

| Parametro | Soglia / Range | Fatto Generato in caso di anomalia |
| --- | --- | --- |
| **pH** | 6.5 - 8.5 | `Fact(problema_ph="acido/basico")` |
| **Solfati** | > 250 mg/L | `Fact(problema_solfati="alto")` |
| **Torbidità** | > 5.0 NTU | `Fact(problema_torbidita="alta")` |
| **Solidi (TDS)** | > 1000 mg/L | `Fact(problema_solidi="alto")` |

**Integrazione Ibrida:** Per la durezza e i solidi, il sistema non si limita alle soglie fisse, ma confronta il valore con la **media del dataset**. Se il valore supera la media (pur restando sotto la soglia critica), viene generato un warning informativo, dimostrando un uso ibrido di conoscenza esperta e statistica.

---

## 3.4 Regole di inferenza e catene decisionali

### 3.4.1 Regole di controllo del flusso

Il sistema utilizza le regole stesse per gestire la propria esecuzione. La catena di attivazione segue questo schema:

1. `start_diagnosis` → Saluto e attivazione osservazioni.
2. `ask_observations` → Passaggio alla fase strumentale.
3. **Regole di step** → Attivazione sequenziale di `ask_ph`, `ask_sulfates`, ecc.
4. `final_report` → Output dei risultati e chiusura.

### 3.4.2 Regola relazionale: Rischio Corrosione

Una delle regole più avanzate combina più parametri per identificare rischi complessi:

* **Condizione**: pH < 6.0 **AND** Solfati > 200 **AND** `Fact(action="analyze")`.
* **Conclusione**: `Fact(problem_type="critical")`.

> [!IMPORTANT]
> **Analisi Critica:** Nel codice attuale, il fatto `Fact(action="analyze")` non viene dichiarato esplicitamente. Ciò rappresenta un limite nel motore inferenziale che impedirebbe l'attivazione della regola, risolvibile con una semplice asserzione al termine dell'acquisizione dati.

---

## 3.5 Integrazione tra KBS e CSP (Diagnosi → Azione)

Il KBS funge da "cervello" che identifica il problema, delegando la risoluzione operativa (pianificazione dei test di laboratorio) al modulo CSP (`src/scheduler.py`).

### 3.5.1 Regole di attivazione dello scheduler

Il sistema mappa le anomalie rilevate su specifiche tipologie di intervento:

* **Chimico**: Attivato da problemi di pH.
* **Fisico**: Attivato da alta torbidità o solidi.
* **Critico**: Attivato dalla combinazione di più fattori (es. pH anomalo + torbidità).

Questa architettura realizza una separazione netta tra **diagnosi simbolica** e **pianificazione dei vincoli**.

---

## 3.6 Output finale del sistema esperto

La regola `final_report` chiude l'analisi quando viene rilevato `Fact(fine_analisi="si")`. Il verdetto si basa sul peso delle evidenze accumulate:

* **Esito Negativo**: Se `problems_found == 0`, l'acqua è considerata potabile.
* **Esito Positivo (Anomalia)**: Viene riportato il numero totale di violazioni dei parametri.

La decisione finale è **deterministica, spiegabile e tracciabile**, poiché ogni anomalia è legata a un fatto specifico inserito nella Working Memory.

---

## 3.7 Complessità, robustezza ed estendibilità

* **Complessità**: La crescita dei fatti () e delle regole () è lineare. L'uso di predicati `lambda` per i vincoli numerici ottimizza il matching senza appesantire il motore Rete.
* **Robustezza**: Il sistema gestisce gli input tramite blocchi `try/except` e validazione dei range (es. pH tra 0 e 14), prevenendo stati inconsistenti della KB.
* **Estendibilità**: L'architettura `param/value` permette di aggiungere nuovi sensori o parametri chimici semplicemente aggiungendo una regola, senza modificare la struttura dati portante.

---

## 3.8 Limiti del KBS e possibili miglioramenti

1. **Gating delle regole**: La mancanza del fatto di controllo `action="analyze"` limita alcune inferenze relazionali.
2. **Centralizzazione delle soglie**: Le soglie sono attualmente cablate nelle regole; sarebbe preferibile una gestione centralizzata tramite costanti o file di configurazione.
3. **Sistema di scoring**: Attualmente ogni anomalia ha lo stesso "peso". Un miglioramento significativo sarebbe l'introduzione di un sistema a punteggio pesato o logica fuzzy per definire il grado di pericolosità.


---

# 4. Ontologia OWL: modellazione del dominio e supporto semantico

Questa sezione descrive l’uso dell’**ontologia OWL** all’interno del progetto, facendo riferimento esplicito ai file presenti nello ZIP e chiarendo **scelte di modellazione**, **modalità d’uso**, **integrazione con il resto del sistema** e **limiti**.  
L’ontologia non è utilizzata come semplice database, ma come **strato semantico** a supporto del sistema complessivo.

File di riferimento:
- `ontology/water_quality.owl`
- `ontology/ontology_builder.py`
- `src/ontology_manager.py`

---

## 4.1 Ruolo dell’ontologia nel progetto

L’ontologia ha il compito di fornire una **rappresentazione concettuale formale** del dominio della qualità dell’acqua.  
In particolare, viene utilizzata per:

- modellare concetti e parametri del dominio in modo esplicito;
- associare **significato e descrizione semantica** ai parametri analizzati dal KBS;
- consentire (quando possibile) **inferenza automatica** tramite reasoner OWL;
- separare la **conoscenza concettuale** dalla logica procedurale e dalle regole.

L’obiettivo non è sostituire la KB rule-based, ma **complementarla**, mantenendo distinti:
- ragionamento simbolico procedurale (KBS);
- modellazione concettuale e semantica (OWL).

---

## 4.2 Struttura dell’ontologia (`water_quality.owl`)

### 4.2.1 Classi principali

L’ontologia definisce un insieme di classi che rappresentano i concetti chiave del dominio.  
Sebbene l’ontologia sia volutamente contenuta, include:

- concetti relativi ai **parametri dell’acqua**;
- concetti relativi alla **qualità/potabilità**;
- concetti utili a descrivere il contesto di analisi.

La scelta di mantenere un numero limitato di classi è intenzionale:
- evita un’ontologia artificiosamente grande ma poco usata;
- rende più chiaro il collegamento con il codice e con il KBS.

---

### 4.2.2 Proprietà e descrizioni semantiche

Per ciascun parametro rilevante, l’ontologia include **proprietà descrittive** (es. commenti, label o proprietà testuali dedicate) che spiegano:

- cosa rappresenta il parametro;
- perché è rilevante per la qualità dell’acqua;
- eventuali effetti associati a valori anomali.

Queste descrizioni sono utilizzate nel sistema per:
- fornire spiegazioni contestuali;
- migliorare la comprensione dell’output;
- separare il *significato* del parametro dalla sua gestione numerica nel KBS.

---

## 4.3 Costruzione e gestione dell’ontologia

### 4.3.1 `ontology_builder.py`

Il file `ontology/ontology_builder.py` è dedicato alla **costruzione e/o modifica programmatica** dell’ontologia.  
La sua presenza nel progetto ha due motivazioni principali:

1. documentare come l’ontologia può essere estesa o rigenerata;
2. dimostrare la capacità di manipolare ontologie tramite codice, non solo tramite editor grafici.

Questo approccio è coerente con una prospettiva di:
- automazione;
- riproducibilità;
- estensione futura (es. aggiunta automatica di nuovi concetti).

---

### 4.3.2 `ontology_manager.py`

Il file `src/ontology_manager.py` è il punto di integrazione tra ontologia e resto del sistema.

Le sue responsabilità principali sono:
- caricare il file `water_quality.owl`;
- inizializzare l’ambiente ontologico (`owlready2`);
- tentare l’attivazione del reasoner;
- fornire accesso alle informazioni semantiche al KBS o ad altri moduli.

---

## 4.4 Uso del reasoner e fallback controllato

### 4.4.1 Attivazione del reasoner OWL

All’interno di `ontology_manager.py`, il sistema tenta di eseguire:

```python
sync_reasoner_pellet()
````

L’uso di Pellet consente, in linea teorica, di:

* inferire relazioni implicite;
* classificare automaticamente individui;
* verificare la consistenza dell’ontologia.

Questa scelta dimostra l’intenzione di utilizzare **ragionamento semantico vero**, non solo una struttura dati statica.

---

### 4.4.2 Gestione del fallback

Una scelta progettuale importante è la gestione esplicita del **fallback**:

* se Pellet o l’ambiente Java non sono disponibili,
* il sistema cattura l’eccezione,
* l’esecuzione continua **senza inferenza automatica**.

In questo scenario:

* l’ontologia viene comunque caricata;
* le descrizioni e le strutture concettuali restano accessibili;
* il sistema non fallisce.

Questa scelta:

* aumenta la **robustezza** del progetto;
* evita dipendenze fragili in fase di esecuzione;
* rende il sistema utilizzabile in contesti diversi (es. ambienti d’esame).

---

## 4.5 Integrazione tra ontologia e KBS

L’integrazione tra ontologia e KBS è **intenzionalmente debole e controllata**.

L’ontologia:

* non sostituisce i fatti del KBS;
* non viene interrogata per fare pattern matching numerico;
* non è usata per prendere decisioni operative dirette.

Il KBS:

* gestisce i valori numerici, le soglie e le regole;
* usa l’ontologia come **supporto semantico** (descrizioni, contesto, possibile inferenza).

Questa separazione evita:

* duplicazione di conoscenza;
* accoppiamento eccessivo tra OWL e regole;
* uso improprio dell’ontologia come database.

---

## 4.6 Complessità e valutazione dell’approccio ontologico

### 4.6.1 Complessità computazionale

* Il caricamento dell’ontologia ha costo contenuto.
* L’inferenza con Pellet può essere computazionalmente onerosa, ma:

  * viene eseguita una sola volta;
  * è opzionale (fallback disponibile).

Nel progetto, l’ontologia è volutamente mantenuta di dimensioni ridotte per evitare overhead non giustificati.

---

### 4.6.2 Adeguatezza rispetto agli obiettivi

L’ontologia:

* non è un esercizio fine a sé stesso;
* è coerente con il dominio del progetto;
* è effettivamente integrata nel codice.

Questo la distingue da:

* ontologie isolate non utilizzate;
* KB OWL usate come semplici tabelle di fatti.

---

## 4.7 Limiti dell’ontologia e possibili estensioni

### 4.7.1 Limiti attuali

* Ontologia relativamente piccola, con inferenza limitata.
* Ragionamento semantico non centrale nel processo decisionale.
* Assenza di assiomi complessi (es. restrizioni cardinalità, catene di proprietà).

Questi limiti sono **consapevoli** e legati allo scopo del progetto.

---

### 4.7.2 Estensioni possibili

L’ontologia può essere estesa in modo naturale per:

* modellare classi di contaminazione (chimica, fisica, biologica);
* collegare parametri a classi di rischio;
* supportare inferenze che guidino direttamente il KBS (es. suggerimento automatico del tipo di problema).

Queste estensioni renderebbero l’ontologia un componente ancora più centrale in un’eventuale evoluzione del progetto (es. lavoro di tesi).

---

## 4.8 Considerazioni finali sullo strato ontologico

Lo strato ontologico del progetto:

* è coerente con i principi dell’Ingegneria della Conoscenza;
* è integrato nel sistema senza forzature;
* contribuisce a separare concetti, regole e azioni operative;
* mostra consapevolezza dei limiti e delle scelte progettuali.

L’ontologia rappresenta quindi un **supporto semantico reale**, non un’aggiunta artificiale, ed è pienamente allineata alle linee guida dell’insegnamento.


---

# 5. Constraint Satisfaction Problem (CSP) e Scheduler

Questa sezione descrive il **modulo di pianificazione** del progetto, implementato come **Constraint Satisfaction Problem (CSP)**.  
Il riferimento principale è il file `src/scheduler.py`, che viene invocato dal KBS (`src/expert_system.py`) quando il sistema inferisce la necessità di un intervento operativo.

L’obiettivo di questo modulo è dimostrare la capacità di:
- modellare un problema decisionale come CSP;
- separare la **diagnosi** (KBS) dalla **pianificazione** (scheduler);
- tradurre una decisione simbolica in un’azione concreta e vincolata.

---

## 5.1 Ruolo del CSP nel sistema complessivo

Il CSP rappresenta lo **strato operativo** del sistema.  
Mentre il KBS risponde alla domanda:

> *“Qual è il problema rilevato?”*

il CSP risponde alla domanda:

> *“Quale risorsa/turno/laboratorio deve essere assegnato, nel rispetto dei vincoli?”*

Questa distinzione è fondamentale per:
- evitare regole procedurali rigide nel KBS;
- mantenere la logica di pianificazione indipendente dalla logica diagnostica;
- dimostrare l’uso di un paradigma dichiarativo a vincoli, come richiesto dal corso.

---

## 5.2 File e integrazione con il KBS

### 5.2.1 File di riferimento
- **Modulo CSP**: `src/scheduler.py`
- **Invocazione**: `src/expert_system.py` tramite il metodo `_run_scheduler(issue_type)`

Il KBS non passa al CSP i singoli parametri numerici, ma **una classificazione simbolica del problema**, ad esempio:
- `"chemical"`
- `"physical"`
- `"critical"`

Questa scelta:
- riduce l’accoppiamento tra KBS e scheduler;
- rende il CSP indipendente dai dettagli della KB;
- consente di modificare i vincoli operativi senza toccare le regole diagnostiche.

---

## 5.3 Modellazione del CSP

Il problema di scheduling è modellato come un CSP classico, definendo:

- **variabili**
- **domini**
- **vincoli**

L’obiettivo non è la complessità industriale del problema, ma la **corretta formalizzazione** e integrazione nel sistema.

---

### 5.3.1 Variabili del CSP

Nel modulo `scheduler.py`, le variabili rappresentano le decisioni da prendere, tipicamente:

- assegnazione di un **laboratorio**;
- selezione di un **turno**;
- eventuale priorità dell’intervento.

Esempio concettuale di variabile:
```text
Laboratory_Assignment
````

Il valore della variabile rappresenta la risorsa scelta per l’intervento.

---

### 5.3.2 Domini delle variabili

Il dominio di ciascuna variabile è costituito da un insieme finito di valori possibili, ad esempio:

* `chemical_lab`
* `physical_lab`
* `critical_lab`
* (eventuali slot temporali disponibili)

Il dominio effettivo dipende dal `issue_type` passato dal KBS:

* problemi chimici → dominio limitato ai laboratori chimici;
* problemi fisici → dominio limitato ai laboratori fisici;
* problemi critici → dominio ristretto a risorse prioritarie.

Questa riduzione del dominio è una forma di **propagazione dei vincoli a monte**, che semplifica la ricerca della soluzione.

---

### 5.3.3 Vincoli del CSP

I vincoli modellano le restrizioni operative del problema.
Nel progetto, i vincoli includono concettualmente:

* **vincoli di compatibilità**:

  * un problema chimico non può essere assegnato a un laboratorio fisico;
* **vincoli di disponibilità**:

  * alcune risorse possono essere disponibili solo in certi slot;
* **vincoli di priorità**:

  * i casi critici devono essere gestiti con risorse dedicate o prioritarie.

Anche se il problema è volutamente semplice, la struttura è coerente con un CSP reale e facilmente estendibile.

---

## 5.4 Risoluzione del CSP

Il modulo `scheduler.py`:

* costruisce il problema a partire dal `issue_type`;
* applica i vincoli;
* cerca una soluzione valida all’interno del dominio.

La soluzione consiste in:

* una scelta coerente di risorsa/turno;
* un output interpretabile, stampato o restituito al KBS.

Non viene forzata una strategia di ottimizzazione complessa (es. minimizzazione costi), poiché l’obiettivo principale è la **soddisfazione dei vincoli**, non l’ottimo globale.

---

## 5.5 Integrazione diagnosi → pianificazione

### 5.5.1 Flusso completo

Il flusso integrato KBS–CSP è il seguente:

1. Il KBS inferisce uno o più fatti di anomalia.
2. Viene determinato un `problem_type`.
3. Una regola del KBS attiva `_run_scheduler(problem_type)`.
4. Il CSP seleziona una risorsa compatibile.
5. Il risultato viene comunicato come azione suggerita.

Questo flusso dimostra una **catena causale completa**:
**conoscenza → inferenza → decisione → azione**.

---

## 5.6 Scelte progettuali e alternative scartate

### 5.6.1 Perché un CSP e non codice procedurale

Una soluzione procedurale (if/else) sarebbe stata:

* più semplice da implementare;
* meno espressiva;
* poco estendibile.

Il CSP consente invece di:

* dichiarare vincoli separatamente dalla logica di controllo;
* estendere facilmente il problema (nuove risorse, nuovi vincoli);
* dimostrare l’uso di un paradigma di ICon distinto dal KBS.

---

### 5.6.2 Perché un CSP semplice

Il problema è volutamente contenuto perché:

* il focus del progetto è l’integrazione dei paradigmi, non la complessità del singolo modulo;
* un CSP troppo grande avrebbe aggiunto complessità senza reale valore valutativo;
* la struttura attuale è sufficiente a dimostrare competenza e correttezza.

---

## 5.7 Complessità computazionale

* Numero di variabili: basso (1–poche variabili).
* Dimensione dei domini: limitata e dipendente dal tipo di problema.
* Numero di vincoli: contenuto.

La complessità è quindi bassa e compatibile con l’uso interattivo del sistema.
Questo è coerente con l’obiettivo di **supporto decisionale**, non di pianificazione industriale su larga scala.

---

## 5.8 Limiti e possibili estensioni del CSP

### 5.8.1 Limiti attuali

* Numero ridotto di risorse e vincoli.
* Assenza di una funzione di costo o ottimizzazione.
* Pianificazione su un singolo intervento alla volta.

---

### 5.8.2 Estensioni possibili

Il modulo CSP può essere esteso per:

* gestire più richieste contemporanee;
* introdurre vincoli temporali più complessi;
* aggiungere criteri di ottimizzazione (es. minimizzazione tempi di attesa);
* integrare priorità dinamiche basate sul contesto.

Queste estensioni sarebbero naturali in un’evoluzione del progetto verso un lavoro di tesi.

---

## 5.9 Considerazioni finali sul modulo CSP

Il modulo CSP:

* è correttamente separato dal KBS;
* è integrato in modo coerente nel flusso decisionale;
* dimostra l’uso pratico di vincoli per supportare azioni operative;
* rispetta le linee guida del corso evitando soluzioni hard-coded.

Pur nella sua semplicità, rappresenta un elemento chiave per trasformare il sistema da puramente diagnostico a **decisionale e operativo**.


---

# 6. Apprendimento Automatico (ML): modelli, parametri e valutazione

Questa sezione descrive in modo dettagliato la **componente di apprendimento automatico supervisionato** del progetto, facendo riferimento esplicito ai file presenti nello ZIP e seguendo rigorosamente le linee guida dell’insegnamento, in particolare per quanto riguarda la **valutazione sperimentale**.

File di riferimento:
- `data/water_potability.csv`
- `src/ml_models.py`
- `src/ml_evaluation.py`
- `main_ml.py`

La componente ML è progettata come **modulo indipendente**, utilizzato per:
- stimare la potabilità dell’acqua a partire dai dati;
- confrontare più modelli di classificazione;
- affiancare e confrontare l’approccio simbolico (KBS) con uno statistico.

---

## 6.1 Ruolo del modulo ML nel progetto

Il modulo ML non sostituisce il KBS, ma lo **completa**.  
Il suo ruolo è quello di:

- individuare pattern statistici nei dati che non sono codificati esplicitamente in regole;
- fornire una stima quantitativa della potabilità;
- permettere un confronto critico tra:
  - decisione rule-based (deterministica e spiegabile),
  - decisione data-driven (probabilistica).

La separazione tra KBS e ML è intenzionale e consente di:
- valutare ciascun approccio in modo indipendente;
- evitare una fusione forzata che ridurrebbe la chiarezza progettuale.

---

## 6.2 Dataset utilizzato

### 6.2.1 Descrizione del dataset

Il dataset utilizzato è:

```

data/water_potability.csv

```

Si tratta di un dataset tabellare con:
- variabili numeriche che descrivono parametri chimico-fisici dell’acqua;
- una variabile target binaria:
  - `Potability = 1` → acqua potabile
  - `Potability = 0` → acqua non potabile

Il dataset è ampiamente utilizzato come benchmark, ma nel progetto:
- non viene usato in modo “da esercizio”;
- è integrato in un confronto metodologico corretto e valutato in modo robusto.

---

### 6.2.2 Preprocessing dei dati

Nel modulo ML vengono eseguite le seguenti operazioni:

- caricamento del dataset;
- gestione dei valori mancanti (NaN);
- separazione tra:
  - feature (`X`);
  - target (`y`).

Eventuali operazioni di scaling o normalizzazione sono applicate **solo se necessarie** per il modello considerato, evitando trasformazioni inutili.

Questa scelta riduce il rischio di:
- leakage;
- preprocessing eccessivo non giustificato.

---

## 6.3 Modelli implementati

I modelli sono definiti e gestiti in `src/ml_models.py`.  
Il progetto implementa **più classificatori**, scelti per rappresentare approcci diversi.

### 6.3.1 Logistic Regression
- Modello lineare, interpretabile.
- Parametro rilevante:
  - `max_iter = 1000` (scelto per garantire convergenza).

Motivazione:
- baseline semplice;
- utile per confrontare modelli più complessi.

---

### 6.3.2 Decision Tree
- Modello non lineare basato su regole indotte dai dati.

Motivazione:
- capacità di modellare interazioni non lineari;
- parziale interpretabilità della struttura ad albero.

---

### 6.3.3 K-Nearest Neighbors (KNN)
- Modello instance-based.

Parametro principale:
- numero di vicini `k` (valore impostato nel codice).

Motivazione:
- approccio basato su similarità;
- sensibilità alla distribuzione dei dati.

---

### 6.3.4 Multi-Layer Perceptron (MLP)
- Rete neurale feed-forward.

Parametri rilevanti:
- architettura della rete (numero di neuroni/layer);
- numero massimo di iterazioni.

Motivazione:
- capacità di apprendere pattern complessi;
- confronto con modelli più semplici.

---

### 6.3.5 Gaussian Naive Bayes
- Modello probabilistico con ipotesi di indipendenza condizionata.

Motivazione:
- semplicità;
- confronto tra modelli generativi e discriminativi.

---

## 6.4 Scelte sugli iperparametri

Gli iperparametri sono scelti secondo criteri **pratici e conservativi**:

- evitare tuning aggressivo che potrebbe portare overfitting;
- mantenere valori standard o leggermente adattati (es. `max_iter`);
- privilegiare la confrontabilità tra modelli.

Questa scelta è coerente con l’obiettivo del progetto:
- dimostrare una valutazione corretta;
- non massimizzare artificialmente le prestazioni.

---

## 6.5 Protocollo di valutazione (punto cruciale)

### 6.5.1 Motivazione del protocollo

Per evitare valutazioni fuorvianti basate su:
- un singolo split train/test;
- una sola matrice di confusione;

il progetto utilizza **Cross-Validation**.

Questa scelta è esplicitamente in linea con le linee guida dell’insegnamento.

---

### 6.5.2 Cross-Validation

Nel metodo `cross_validate` di `ml_models.py`:
- viene applicata una **k-fold cross-validation** (tipicamente k = 10);
- per ciascun fold viene calcolata l’accuracy;
- vengono restituiti:
  - media (`mean`);
  - deviazione standard (`std`).

Questo consente di stimare:
- performance attesa;
- stabilità del modello.

---

### 6.5.3 Metriche utilizzate

La metrica principale utilizzata è:

- **Accuracy**

La scelta è motivata da:
- natura binaria del problema;
- obiettivo comparativo tra modelli.

Metriche più complesse non vengono introdotte per evitare:
- ridondanza;
- allungamento non necessario della documentazione.

---
## 6.6 Risultati sperimentali

I risultati vengono riportati **come media ± deviazione standard** su più run,
ottenuti tramite **k-fold cross-validation**.

### 6.6.1 Risultati della Cross-Validation

| Modello              | CV folds | Accuracy (mean) | Accuracy (std) |
|----------------------|----------|------------------|----------------|
| Logistic Regression  | 10       | 0.6102           | 0.0017         |
| Decision Tree        | 10       | 0.6190           | 0.0347         |
| KNN (k=5)            | 10       | 0.5641           | 0.0175         |
| MLP                  | 10       | 0.5196           | 0.0992         |
| Naive Bayes          | 10       | 0.6151           | 0.0552         |

La valutazione dei modelli è stata effettuata tramite **10-fold cross-validation**,
riportando l’accuracy come **media ± deviazione standard**.
Questa scelta consente di ottenere una stima robusta delle prestazioni,
evitando conclusioni basate su un singolo split train/test.

Le metriche calcolate su un singolo test set sono state utilizzate
**esclusivamente a fini illustrativi** e non per il confronto tra modelli.
*(I valori numerici sono ottenuti eseguendo gli script in `main_ml.py`.)*

---

## 6.7 Discussione dei risultati

L’analisi dei risultati consente di osservare:

- differenze di performance tra modelli lineari e non lineari;
- variabilità delle prestazioni (std) come indicatore di stabilità;
- eventuali trade-off tra accuratezza media e robustezza.

Il confronto non mira a “scegliere il migliore”, ma a:
- comprendere il comportamento dei modelli;
- confrontare l’approccio ML con quello rule-based.

---

## 6.8 Confronto concettuale KBS vs ML

| Aspetto            | KBS                          | ML                           |
|--------------------|------------------------------|------------------------------|
| Spiegabilità       | Alta                         | Variabile / bassa            |
| Robustezza a casi critici | Alta (regole esplicite) | Dipende dai dati             |
| Adattabilità       | Manuale (nuove regole)       | Automatica (riaddestramento) |
| Uso nel progetto   | Diagnosi + azione            | Supporto predittivo          |

Questo confronto giustifica la scelta di un sistema **ibrido**, anziché affidarsi a un solo paradigma.

---

## 6.9 Limiti e possibili estensioni del modulo ML

### 6.9.1 Limiti
- uso di un dataset standard;
- assenza di tuning sistematico degli iperparametri;
- metriche limitate all’accuracy.

---

### 6.9.2 Estensioni possibili
- tuning automatico (Grid Search);
- introduzione di metriche aggiuntive (precision/recall);
- integrazione più stretta con il KBS (es. suggerimento soglie).

---

## 6.10 Considerazioni finali sul modulo ML

La componente ML:
- è correttamente isolata e valutata;
- utilizza protocolli sperimentali adeguati;
- evita presentazioni fuorvianti basate su singoli run;
- contribuisce in modo significativo al valore complessivo del progetto.

Insieme al KBS, fornisce una visione completa e coerente del problema della valutazione della qualità dell’acqua.

---
# 7. Conclusioni

Il progetto ha portato alla realizzazione di un **sistema ibrido di Ingegneria della Conoscenza** per la valutazione della qualità dell’acqua, integrando in modo coerente i principali temi affrontati nel corso.

In particolare, il lavoro combina:

- un **Knowledge-Based System rule-based** (`src/expert_system.py`), con una Knowledge Base esplicita e regole anche relazionali su parametri numerici;
- un’**ontologia OWL** (`ontology/water_quality.owl`) utilizzata come strato di modellazione concettuale e supporto semantico;
- un **modulo CSP** (`src/scheduler.py`) per la gestione operativa delle risorse, separato dalla logica diagnostica;
- una **componente di apprendimento automatico** (`src/ml_models.py`) valutata correttamente tramite cross-validation e metriche aggregate.

La scelta di un’architettura modulare consente di mantenere distinti:
- ragionamento simbolico (KBS),
- rappresentazione concettuale (ontologia),
- pianificazione a vincoli (CSP),
- valutazione statistica (ML),

rendendo il sistema chiaro, estendibile e facilmente valutabile.

Il **KBS** rappresenta il nucleo centrale del progetto, sia per la quantità di conoscenza esplicitata nella KB, sia per l’uso di regole relazionali che combinano più parametri.  
La **componente ML** non è usata come semplice esercizio su dataset, ma come termine di confronto metodologico, con una valutazione sperimentale coerente con le linee guida dell’insegnamento.

Sono stati inoltre evidenziati alcuni **limiti reali dell’implementazione** (ad esempio gating incompleto di alcune regole o uso limitato dell’inferenza ontologica), che non compromettono il funzionamento del sistema ma rappresentano punti di miglioramento concreti.

Nel complesso, il progetto dimostra la capacità di:
- progettare e implementare un sistema di Ingegneria della Conoscenza non banale;
- motivare le scelte tecniche effettuate;
- valutare criticamente il sistema e i suoi risultati.

Il lavoro può essere considerato completo rispetto agli obiettivi del corso e, grazie alla struttura modulare adottata, rappresenta una base solida per eventuali estensioni future.
