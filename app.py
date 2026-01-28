import streamlit as st
import pandas as pd
import collections.abc
import collections

# --- FIX COMPATIBILITÀ PYTHON 3.10+ (Per Experta) ---
if not hasattr(collections, 'Mapping'): collections.Mapping = collections.abc.Mapping
if not hasattr(collections, 'MutableMapping'): collections.MutableMapping = collections.abc.MutableMapping
if not hasattr(collections, 'Iterable'): collections.Iterable = collections.abc.Iterable

from experta import *
from src.scheduler import laboratory_csp
from src.bayesian_model import WaterRiskBayesianNetwork
# Importiamo il manager ontologico (con l'alias corretto)
from src.ontology_manager import manager as water_ontology

# --- CLASSE ESPERTO PER GUI (Tutte le regole ripristinate) ---
class WaterExpertGUI(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.msgs = []
        self.csp_suggestion = None 
        self.problems_count = 0

    def log(self, message, type="info"):
        self.msgs.append({"msg": message, "type": type})

    @DefFacts()
    def _initial_action(self):
        yield Fact(inizio="si")

    # 1. ANALISI pH
    @Rule(Fact(param='ph', value=MATCH.val))
    def check_ph(self, val):
        if val < 6.5:
            self.log(f"🔴 pH ACIDO rilevato ({val}). Corrosivo!", "error")
            self.declare(Fact(problema_ph="acido"))
            self.problems_count += 1
        elif val > 8.5:
            self.log(f"🔴 pH BASICO rilevato ({val}).", "error")
            self.declare(Fact(problema_ph="basico"))
            self.problems_count += 1
        else:
            self.log("✅ pH nella norma.", "success")

    # 2. ANALISI SOLFATI
    @Rule(Fact(param='sulfate', value=MATCH.val))
    def check_sulfate(self, val):
        if val > 250:
            self.log(f"⚠️ Solfati ALTI ({val} mg/L).", "warning")
            self.declare(Fact(problema_solfati="alto"))
            self.problems_count += 1
        else:
            self.log("✅ Solfati nella norma.", "success")

    # 3. ANALISI TORBIDITÀ (La regola che mancava!)
    @Rule(Fact(param='turbidity', value=MATCH.val))
    def check_turbidity(self, val):
        if val > 5.0:
            self.log(f"🔴 Torbidità ALTA ({val} NTU). Acqua sporca.", "error")
            self.declare(Fact(problema_torbidita="alta"))
            self.problems_count += 1
        else:
            self.log("✅ Torbidità nella norma.", "success")

    # 4. ANALISI SOLIDI (TDS) - Ripristinata
    @Rule(Fact(param='solids', value=MATCH.val))
    def check_solids(self, val):
        if val > 1000:
            self.log(f"🔴 TDS Alto ({val} ppm). Acqua troppo mineralizzata.", "error")
            self.declare(Fact(problema_solidi="alto"))
            self.problems_count += 1

    # 5. ANALISI DUREZZA - Ripristinata
    @Rule(Fact(param='hardness', value=MATCH.val))
    def check_hardness(self, val):
        if val > 300:
            self.log(f"ℹ️ Acqua dura ({val} mg/L). Possibili incrostazioni.", "info")

    # 6. REGOLE RELAZIONALI (Combinazioni)
    @Rule(Fact(param='ph', value=P(lambda x: x < 6.0)),
          Fact(param='sulfate', value=P(lambda x: x > 200)))
    def corrosion_risk(self):
        self.log("🔥 COMBINAZIONE CRITICA: pH Acido + Solfati Alti! Rischio corrosione tubature.", "error")
        self.declare(Fact(problem_type="critical"))

    # 7. ATTIVAZIONE SCHEDULER (CSP)
    # Laboratorio Chimico (pH o Solfati)
    @Rule(OR(Fact(problema_ph="acido"), Fact(problema_ph="basico"), Fact(problema_solfati="alto")))
    def schedule_chemical(self):
        if self.csp_suggestion != "critical":
            self.csp_suggestion = "chemical"

    # Laboratorio Fisico (Torbidità o Solidi)
    @Rule(OR(Fact(problema_torbidita="alta"), Fact(problema_solidi="alto")))
    def schedule_physical(self):
        if self.csp_suggestion != "critical":
            self.csp_suggestion = "physical"

    # Squadra Emergenza (Problemi Critici)
    @Rule(Fact(problem_type="critical"))
    def schedule_critical(self):
        self.csp_suggestion = "critical"


# --- INTERFACCIA GRAFICA STREAMLIT ---
st.set_page_config(page_title="Water Quality DSS", layout="wide", page_icon="💧")

st.title("💧 Water Quality Assessment System")
st.markdown("Sistema Ibrido: **KBS (Regole)** + **Ontologia (Semantica)** + **Bayes (Probabilità)** + **CSP (Turni)**")

# --- COLONNA LATERALE (INPUT COMPLETI) ---
with st.sidebar:
    st.header("1. Dati Sensori")
    # Tutti i parametri del programma originale
    ph_input = st.slider("pH (0-14)", 0.0, 14.0, 7.0, help="Range ottimale: 6.5 - 8.5")
    sulfate_input = st.number_input("Solfati (mg/L)", 0.0, 500.0, 200.0, step=10.0)
    turbidity_input = st.slider("Torbidità (NTU)", 0.0, 10.0, 3.0, help="Max: 5.0")
    solids_input = st.number_input("Solidi Totali (TDS ppm)", 0.0, 5000.0, 500.0, step=50.0)
    hardness_input = st.number_input("Durezza (mg/L)", 0.0, 500.0, 150.0, step=10.0)
    
    st.header("2. Osservazioni Qualitative")
    # Le domande "tante cose" che mancavano
    obs_smell = st.checkbox("Cattivo Odore?")
    obs_taste = st.checkbox("Sapore Sgradevole?")
    
    st.header("3. Contesto Ambientale (Bayes)")
    has_industry = st.checkbox("Industrie Vicine?")
    heavy_rain = st.checkbox("Piogge Intense?")
    
    run_btn = st.button("AVVIA ANALISI 🚀", type="primary", use_container_width=True)

# --- LOGICA ESECUZIONE ---
if run_btn:
    # 1. MODULO BAYESIANO (Stima Rischio a Priori)
    bn = WaterRiskBayesianNetwork()
    risk_prob = bn.get_risk_probability(has_industry, heavy_rain)
    
    # Dashboard Metriche
    col1, col2, col3 = st.columns(3)
    col1.metric("Probabilità Inquinamento (Bayes)", f"{risk_prob*100:.1f}%", delta_color="inverse")
    
    # Avviso Rischio Bayesiano
    if risk_prob > 0.6:
        st.warning(f"⚠️ Attenzione: Il modello probabilistico indica un alto rischio ambientale ({risk_prob:.2f})!")

    st.divider()

    col_kbs, col_onto = st.columns(2)

    with col_kbs:
        st.subheader("🕵️ Diagnosi Sistema Esperto")
        # Inizializza Motore Experta
        engine = WaterExpertGUI()
        engine.reset()
        
        # Caricamento Fatti Numerici
        engine.declare(Fact(param='ph', value=ph_input))
        engine.declare(Fact(param='sulfate', value=sulfate_input))
        engine.declare(Fact(param='turbidity', value=turbidity_input))
        engine.declare(Fact(param='solids', value=solids_input))
        engine.declare(Fact(param='hardness', value=hardness_input))
        
        # Caricamento Fatti Qualitativi (Opzionale per regole future)
        if obs_smell: engine.declare(Fact(cattivo_odore="si"))
        
        engine.run()
        
        # Visualizzazione Messaggi
        if not engine.msgs:
            st.success("✅ Nessuna anomalia rilevata dalle regole.")
        else:
            for item in engine.msgs:
                if item['type'] == 'error': st.error(item['msg'])
                elif item['type'] == 'warning': st.warning(item['msg'])
                else: st.info(item['msg'])

    with col_onto:
        st.subheader("🦉 Analisi Semantica (SWRL)")
        # Analisi Ontologica
        is_corrosive = water_ontology.semantic_check(ph_input, sulfate_input)
        
        if is_corrosive:
            st.error("🛑 **Rilevamento Semantico:** Regola SWRL attivata!")
            st.markdown("""
            Il reasoner ha dedotto che il campione appartiene alla classe **CorrosiveWater**.
            > *Logica: (pH < 6.0 ∧ Solfati > 200) → Corrosive*
            """)
        else:
            st.success("✅ Nessuna classe di pericolo inferita semanticamente.")

    st.divider()

    # 3. PIANIFICAZIONE (CSP)
    st.subheader("📅 Gestione Operativa (CSP Scheduler)")
    
    if engine.csp_suggestion:
        problem_type = engine.csp_suggestion
        st.markdown(f"Tipo Intervento Richiesto: **{problem_type.upper()}**")
        
        # Risoluzione CSP
        csp = laboratory_csp(problem_type)
        solutions = csp.get_solutions_list()
        
        if solutions:
            # Creiamo un DataFrame per una tabella più bella
            data = []
            for sol in solutions:
                # Esempio stringa: "Lunedi - Mattina (08-14): Dr. Rossi"
                parts = sol.split(": ")
                day_turn = parts[0]
                staff = parts[1]
                data.append({"Turno": day_turn, "Personale Assegnato": staff})
            
            st.table(pd.DataFrame(data))
        else:
            st.error("❌ Nessun turno disponibile compatibile con i vincoli!")
    else:
        st.info("👍 Nessun intervento tecnico necessario.")

else:
    st.info("👈 Configura i parametri a sinistra per iniziare.")