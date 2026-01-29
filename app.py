import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import collections.abc
import collections

# --- FIX COMPATIBILITÀ PYTHON 3.10+ ---
if not hasattr(collections, 'Mapping'): collections.Mapping = collections.abc.Mapping
if not hasattr(collections, 'MutableMapping'): collections.MutableMapping = collections.abc.MutableMapping
if not hasattr(collections, 'Iterable'): collections.Iterable = collections.abc.Iterable

from experta import *
from src.scheduler import laboratoryCsp
from src.bayesian_model import WaterRiskBayesianNetwork
from src.ontology_manager import manager as waterOntology
from src.data_loader import waterData
from src.ml_models import (
    waterLogReg, 
    waterDecTree, 
    waterKnn, 
    waterNeuralNetwork, 
    waterNaiveBayes
)
# Importiamo la classe Base che hai creato nel passo precedente
from src.expert_system import BaseWaterExpert 

# --- FUNZIONI DI CACHING (IL PUNTO 2) ---

@st.cache_data
def load_dataset():
    """Carica il dataset una volta sola."""
    return waterData()

@st.cache_resource
def train_and_evaluate_models(_data):
    """
    Esegue il training e la Cross Validation dei modelli.
    Usa cache_resource perché restituisce oggetti complessi (modelli).
    L'argomento _data ha l'underscore per evitare che Streamlit provi a farne l'hashing (lento).
    """
    results_stats = []
    trained_models_list = []
    
    # Configurazione modelli
    models_config = [
        ("Logistic Regression", waterLogReg(_data, 0.2)),
        ("Decision Tree", waterDecTree(_data, 0.2, max_depth=10)),
        ("KNN (k=5)", waterKnn(_data, 0.2, 5)),
        ("Naive Bayes", waterNaiveBayes(_data, 0.2)),
        ("Neural Network", waterNeuralNetwork(_data, 0.2, hidden_layers=(100, 50, 20)))
    ]
    
    for name, model in models_config:
        # 1. Cross Validation (Operazione Lenta)
        try:
            # Gestione robusta del ritorno (tupla o valore singolo)
            res = model.evaluate_with_cross_validation(folds=5)
            if isinstance(res, tuple):
                acc, std = res
            else:
                acc, std = res, 0.0
            
            results_stats.append({"Model": name, "Accuracy": acc, "Std": std})
        except Exception as e:
            results_stats.append({"Model": name, "Accuracy": 0.0, "Std": 0.0, "Error": str(e)})

        # 2. Fit su split singolo (per generare grafici ROC/Confusion Matrix)
        model.predict()
        trained_models_list.append((name, model))
        
    return results_stats, trained_models_list

# --- CLASSE ESPERTO PER GUI ---
class WaterExpertGUI(BaseWaterExpert):
    def __init__(self):
        super().__init__()
        self.msgs = []
        # self.csp_suggestion e self.problems_count sono ereditati dalla Base

    def notify(self, message, msg_type="info"):
        self.msgs.append({"msg": message, "type": msg_type})

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Water Quality DSS", layout="wide", page_icon="💧")
st.title("💧 Water Quality Assessment System")

tab1, tab2 = st.tabs(["🕵️ Sistema Esperto & Decisionale", "🤖 Machine Learning Lab"])

# ==============================================================================
# TAB 1: SISTEMA ESPERTO (AGGIORNATO)
# ==============================================================================
with tab1:
    st.markdown("### Modulo Supporto alle Decisioni (DSS)")
    st.markdown("Analisi basata su **Regole (WHO)**, **Ontologie** e **Probabilità Bayesiana**.")
    
    col_input, col_res = st.columns([1, 2])
    
    with col_input:
        st.info("📊 **Inserimento Parametri**")
        
        # --- NUOVA SEZIONE: OSSERVAZIONI (Fase 1) ---
        with st.expander("Step 1: Osservazione Sensoriale", expanded=True):
            st.caption("Prima dell'analisi, cosa noti?")
            obs_torbida = st.checkbox("Acqua Torbida (Visiva)")
            obs_odore = st.checkbox("Cattivo Odore")
            obs_sapore = st.checkbox("Sapore Metallico")
        
        # --- INPUT DATI STRUMENTALI (Fase 2) ---
        st.markdown("---")
        st.caption("Step 2: Dati Strumentali")
        ph_input = st.slider("pH (0-14)", 0.0, 14.0, 7.0)
        sulfate_input = st.number_input("Solfati (mg/L)", 0.0, 500.0, 200.0)
        turbidity_input = st.slider("Torbidità (NTU)", 0.0, 10.0, 3.0)
        solids_input = st.number_input("Solidi (TDS ppm)", 0.0, 5000.0, 500.0)
        hardness_input = st.number_input("Durezza (mg/L)", 0.0, 500.0, 150.0)
        
        st.markdown("---")
        st.caption("Parametri Avanzati")
        chloramines_input = st.number_input("Cloramine (ppm)", 0.0, 15.0, 4.0)
        conductivity_input = st.number_input("Conducibilità (uS/cm)", 0.0, 1000.0, 400.0)
        organic_input = st.number_input("Carbonio Organico (ppm)", 0.0, 30.0, 10.0)
        thm_input = st.number_input("Trialometani (ug/L)", 0.0, 120.0, 60.0)

        st.markdown("---")
        st.write("**Contesto Bayesiano**")
        has_industry = st.checkbox("Industrie Vicine?")
        heavy_rain = st.checkbox("Piogge Intense?")
        
        analyze_btn = st.button("Avvia Diagnosi", type="primary", use_container_width=True)

    with col_res:
        if analyze_btn:
            # 1. BAYES (Analisi Probabilistica)
            bn = WaterRiskBayesianNetwork()

            # Passiamo TUTTE le evidenze raccolte dai checkbox
            risk_prob = bn.get_risk_probability(
                ind=has_industry,       # Industrie
                rain=heavy_rain,        # Pioggia
                odor=obs_odore,         # Odore
                taste=obs_sapore,       # Sapore
                visual=obs_torbida      # Vista
            )     
                   
            c1, c2 = st.columns(2)
            c1.metric("Probabilità Inquinamento", f"{risk_prob*100:.1f}%")
            
            if risk_prob > 0.8:
                c1.error("☣️ Rischio CRITICO!")
            elif risk_prob > 0.5:
                c1.warning("⚠️ Rischio Elevato")
            else:
                c1.success("✅ Rischio Basso")
            
            # 2. SISTEMA ESPERTO (Analisi Regole)
            engine = WaterExpertGUI()
            engine.reset()
            
            # A. Passiamo le osservazioni (Nuova Funzionalità)
            if obs_torbida: engine.declare(Fact(osservazione_torbida="si"))
            if obs_odore: engine.declare(Fact(osservazione_odore="si"))
            if obs_sapore: engine.declare(Fact(osservazione_sapore="si"))

            # B. Passiamo i dati numerici
            engine.declare(Fact(param='ph', value=ph_input))
            engine.declare(Fact(param='sulfate', value=sulfate_input))
            engine.declare(Fact(param='turbidity', value=turbidity_input))
            engine.declare(Fact(param='solids', value=solids_input))
            engine.declare(Fact(param='hardness', value=hardness_input))
            engine.declare(Fact(param='chloramines', value=chloramines_input))
            engine.declare(Fact(param='conductivity', value=conductivity_input))
            engine.declare(Fact(param='organic_carbon', value=organic_input))
            engine.declare(Fact(param='trihalomethanes', value=thm_input))

            # C. Avviamo il motore
            engine.run()
            
            # D. Mostriamo i messaggi raccolti
            st.subheader("Risultati Analisi")
            
            if not engine.msgs:
                st.success("✅ Nessuna anomalia specifica rilevata dalle regole WHO.")
            else:
                for msg in engine.msgs:
                    if msg['type'] == 'error': 
                        st.error(msg['msg'])
                    elif msg['type'] == 'warning': 
                        st.warning(msg['msg'])
                    elif msg['type'] == 'success':
                        st.success(msg['msg'])
                    else: 
                        st.info(msg['msg'])

            # 3. ONTOLOGIA (Analisi Semantica)
            # Nota: Assicurati che water_ontology sia importato correttamente in alto
            try:
                is_corrosive = waterOntology.semantic_check(ph_input, sulfate_input)
                if is_corrosive:
                    st.error("🛑 **Ontologia SWRL:** Acqua classificata come 'CorrosiveWater'.")
            except Exception as e:
                st.warning(f"Modulo Ontologia non attivo o errore: {e}")
            
            # 4. CSP SCHEDULER (Pianificazione)
            # Se il sistema esperto suggerisce un intervento (engine.csp_suggestion non è None)
            if engine.csp_suggestion:
                st.markdown("---")
                st.subheader(f"📅 Pianificazione Intervento: {engine.csp_suggestion.upper()}")
                
                # Chiama il tuo scheduler aggiornato con i vincoli
                csp = laboratoryCsp(engine.csp_suggestion)
                solutions = csp.get_solutions_list()
                
                if solutions:
                    st.write("Turni disponibili (filtrati per competenza e orari):")
                    # Visualizzazione semplice come lista, dato che ora sono stringhe formattate
                    for sol in solutions:
                        st.text(sol) 
                else:
                    st.error("❌ Nessun tecnico disponibile per i vincoli attuali (es. Orario chiusura laboratorio).")
            else:
                st.markdown("---")
                st.info("ℹ️ Nessuna manutenzione necessaria al momento.")

# ==============================================================================
# TAB 2: MACHINE LEARNING (OTTIMIZZATO CON CACHE)
# ==============================================================================
with tab2:
    st.markdown("### 🤖 Laboratorio Machine Learning")
    
    # Caricamento Dataset (Cached)
    data = load_dataset()
    st.write(f"Dataset caricato: **{len(data.get_data())}** campioni.")

    # Bottone di avvio
    if st.button("🚀 Esegui Analisi ML", type="primary"):
        
        with st.spinner("Addestramento modelli in corso... (la prima volta richiede qualche secondo)"):
            # Chiamata alla funzione CACHED:
            # - La prima volta esegue il codice.
            # - Le volte successive restituisce subito il risultato salvato.
            results_stats, trained_models = train_and_evaluate_models(data)
            
            # --- Visualizzazione ---
            for name, model in trained_models:
                st.markdown(f"#### 🔹 {name}")
                
                # Recuperiamo le statistiche calcolate
                stat = next((item for item in results_stats if item["Model"] == name), None)
                if stat:
                    st.write(f"**Accuracy Media (CV):** {stat['Accuracy']:.4f} (± {stat['Std']:.4f})")
                
                gc1, gc2 = st.columns(2)
                
                # Matrice Confusione
                with gc1:
                    if model.y_test is not None:
                        from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
                        cm = confusion_matrix(model.y_test, model.y_predicted)
                        fig_cm, ax_cm = plt.subplots()
                        disp = ConfusionMatrixDisplay(confusion_matrix=cm)
                        disp.plot(cmap="Blues", ax=ax_cm)
                        ax_cm.set_title(f"Confusion Matrix")
                        st.pyplot(fig_cm)
                
                # ROC Curve
                with gc2:
                    if hasattr(model.model, "predict_proba"):
                        from sklearn.metrics import roc_curve, auc
                        y_probs = model.model.predict_proba(model.x_test)[:, 1]
                        fpr, tpr, _ = roc_curve(model.y_test, y_probs)
                        roc_auc = auc(fpr, tpr)
                        
                        fig_roc, ax_roc = plt.subplots()
                        ax_roc.plot(fpr, tpr, color='darkorange', lw=2, label=f'AUC = {roc_auc:.2f}')
                        ax_roc.plot([0, 1], [0, 1], color='navy', linestyle='--')
                        ax_roc.set_title(f"ROC Curve")
                        ax_roc.legend(loc="lower right")
                        st.pyplot(fig_roc)
                    else:
                        st.info("ROC Curve non disponibile per questo modello.")
                st.divider()

            # CONFRONTO FINALE
            st.subheader("🏆 Confronto Finale Accuratezza")
            df_res = pd.DataFrame(results_stats)
            
            if not df_res.empty:
                fig_bar, ax_bar = plt.subplots(figsize=(10, 5))
                sns.barplot(x="Model", y="Accuracy", data=df_res, palette="viridis", ax=ax_bar)
                ax_bar.set_ylim(0, 1.0)
                for i, row in df_res.iterrows():
                    ax_bar.text(float(i), row.Accuracy + 0.01, f"{row.Accuracy:.2f}", color='black', ha="center")
                st.pyplot(fig_bar)