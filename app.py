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
from src.scheduler import laboratory_csp
from src.bayesian_model import WaterRiskBayesianNetwork
from src.ontology_manager import manager as water_ontology
from src.data_loader import water_data
from src.ml_models import (
    water_log_reg, 
    water_dec_tree, 
    water_knn, 
    water_neural_network, 
    water_naive_bayes
)

# --- CLASSE ESPERTO PER GUI ---
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

    @Rule(Fact(param='sulfate', value=MATCH.val))
    def check_sulfate(self, val):
        if val > 250:
            self.log(f"⚠️ Solfati ALTI ({val} mg/L).", "warning")
            self.declare(Fact(problema_solfati="alto"))
            self.problems_count += 1
        else:
            self.log("✅ Solfati nella norma.", "success")

    @Rule(Fact(param='turbidity', value=MATCH.val))
    def check_turbidity(self, val):
        if val > 5.0:
            self.log(f"🔴 Torbidità ALTA ({val} NTU). Acqua sporca.", "error")
            self.declare(Fact(problema_torbidita="alta"))
            self.problems_count += 1
        else:
            self.log("✅ Torbidità nella norma.", "success")

    @Rule(Fact(param='solids', value=MATCH.val))
    def check_solids(self, val):
        if val > 1000:
            self.log(f"🔴 TDS Alto ({val} ppm). Acqua troppo mineralizzata.", "error")
            self.declare(Fact(problema_solidi="alto"))
            self.problems_count += 1

    @Rule(Fact(param='hardness', value=MATCH.val))
    def check_hardness(self, val):
        if val > 300:
            self.log(f"ℹ️ Acqua dura ({val} mg/L). Possibili incrostazioni.", "info")

    @Rule(Fact(param='ph', value=P(lambda x: x < 6.0)),
          Fact(param='sulfate', value=P(lambda x: x > 200)))
    def corrosion_risk(self):
        self.log("🔥 COMBINAZIONE CRITICA: pH Acido + Solfati Alti! Rischio corrosione tubature.", "error")
        self.declare(Fact(problem_type="critical"))

    @Rule(OR(Fact(problema_ph="acido"), Fact(problema_ph="basico"), Fact(problema_solfati="alto")))
    def schedule_chemical(self):
        if self.csp_suggestion != "critical":
            self.csp_suggestion = "chemical"

    @Rule(OR(Fact(problema_torbidita="alta"), Fact(problema_solidi="alto")))
    def schedule_physical(self):
        if self.csp_suggestion != "critical":
            self.csp_suggestion = "physical"

    @Rule(Fact(problem_type="critical"))
    def schedule_critical(self):
        self.csp_suggestion = "critical"


# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Water Quality DSS", layout="wide", page_icon="💧")
st.title("💧 Water Quality Assessment System")

# CREAZIONE TAB (SCHEDE)
tab1, tab2 = st.tabs(["🕵️ Sistema Esperto & Decisionale", "🤖 Machine Learning Lab"])

# ==============================================================================
# TAB 1: SISTEMA ESPERTO (Logica di main_expert.py + main_expert_gui)
# ==============================================================================
with tab1:
    st.markdown("### Modulo Supporto alle Decisioni (DSS)")
    st.markdown("Analisi basata su **Regole (WHO)**, **Ontologie** e **Probabilità Bayesiana**.")
    
    col_input, col_res = st.columns([1, 2])
    
    with col_input:
        st.info("📊 **Inserimento Parametri**")
        ph_input = st.slider("pH (0-14)", 0.0, 14.0, 7.0)
        sulfate_input = st.number_input("Solfati (mg/L)", 0.0, 500.0, 200.0)
        turbidity_input = st.slider("Torbidità (NTU)", 0.0, 10.0, 3.0)
        solids_input = st.number_input("Solidi (TDS ppm)", 0.0, 5000.0, 500.0)
        hardness_input = st.number_input("Durezza (mg/L)", 0.0, 500.0, 150.0)
        
        st.markdown("---")
        st.write("**Contesto Bayesiano**")
        has_industry = st.checkbox("Industrie Vicine?")
        heavy_rain = st.checkbox("Piogge Intense?")
        
        analyze_btn = st.button("Avvia Diagnosi", type="primary", use_container_width=True)

    with col_res:
        if analyze_btn:
            # 1. BAYES
            bn = WaterRiskBayesianNetwork()
            risk_prob = bn.get_risk_probability(has_industry, heavy_rain)
            
            c1, c2 = st.columns(2)
            c1.metric("Probabilità Inquinamento", f"{risk_prob*100:.1f}%")
            if risk_prob > 0.6:
                c1.warning("⚠️ Rischio Ambientale Elevato!")
            
            # 2. SISTEMA ESPERTO
            engine = WaterExpertGUI()
            engine.reset()
            engine.declare(Fact(param='ph', value=ph_input))
            engine.declare(Fact(param='sulfate', value=sulfate_input))
            engine.declare(Fact(param='turbidity', value=turbidity_input))
            engine.declare(Fact(param='solids', value=solids_input))
            engine.declare(Fact(param='hardness', value=hardness_input))
            engine.run()
            
            st.subheader("Risultati Analisi")
            
            # Visualizzazione messaggi regole
            if not engine.msgs:
                st.success("Nessuna anomalia specifica rilevata dalle regole WHO.")
            else:
                for msg in engine.msgs:
                    if msg['type'] == 'error': st.error(msg['msg'])
                    elif msg['type'] == 'warning': st.warning(msg['msg'])
                    else: st.info(msg['msg'])

            # 3. ONTOLOGIA
            is_corrosive = water_ontology.semantic_check(ph_input, sulfate_input)
            if is_corrosive:
                st.error("🛑 **Ontologia SWRL:** Acqua classificata come 'CorrosiveWater'.")
            
            # 4. CSP SCHEDULER
            if engine.csp_suggestion:
                st.markdown("---")
                st.subheader("📅 Pianificazione Intervento")
                csp = laboratory_csp(engine.csp_suggestion)
                solutions = csp.get_solutions_list()
                
                if solutions:
                    df_sched = pd.DataFrame([s.split(": ") for s in solutions], columns=["Turno", "Staff"])
                    st.table(df_sched)
                else:
                    st.error("Nessun tecnico disponibile per i vincoli attuali.")

# ==============================================================================
# TAB 2: MACHINE LEARNING (Logica di main_ml.py)
# ==============================================================================
with tab2:
    st.markdown("### 🤖 Laboratorio Machine Learning")
    st.markdown("Addestramento modelli sul dataset `water_potability.csv`.")
    
    if st.button("🚀 Avvia Training e Confronto Modelli", key="train_btn"):
        with st.spinner("Caricamento dati e addestramento in corso... (potrebbe richiedere qualche secondo)"):
            
            # 1. Caricamento Dati
            data = water_data()
            results = []
            
            # Lista modelli
            models_list = [
                ("Logistic Regression", water_log_reg(data, 0.2)),
                ("Decision Tree", water_dec_tree(data, 0.2)),
                ("KNN (k=5)", water_knn(data, 0.2, 5)),
                ("Naive Bayes", water_naive_bayes(data, 0.2)),
                ("Neural Network", water_neural_network(data, 0.2))
            ]
            
            # Colonne per i risultati
            st.write(f"Dataset caricato: **{len(data.get_data())}** campioni.")
            
            # Creiamo i grafici per ogni modello
            for name, model in models_list:
                st.markdown(f"#### 🔹 {name}")
                
                # Cross Validation veloce (per non bloccare troppo la UI riduciamo i fold se necessario)
                # Qui usiamo la logica del main_ml.py
                try:
                    acc, std = model.evaluate_with_cross_validation(folds=5)
                    st.write(f"**Accuracy Media (CV):** {acc:.4f} (± {std:.4f})")
                    results.append({"Model": name, "Accuracy": acc})
                except Exception as e:
                    st.error(f"Errore CV: {e}")

                # Training su Split singolo per grafici
                model.predict()
                
                # Grafici in colonne
                gc1, gc2 = st.columns(2)
                
                # Matrice Confusione
                with gc1:
                    if model.y_test is not None:
                        from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
                        cm = confusion_matrix(model.y_test, model.y_predicted)
                        fig_cm, ax_cm = plt.subplots()
                        disp = ConfusionMatrixDisplay(confusion_matrix=cm)
                        disp.plot(cmap="Blues", ax=ax_cm)
                        ax_cm.set_title(f"Confusion Matrix - {name}")
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
                        ax_roc.set_title(f"ROC Curve - {name}")
                        ax_roc.legend(loc="lower right")
                        st.pyplot(fig_roc)
                    else:
                        st.info("ROC Curve non disponibile per questo modello.")
                
                st.divider()

            # CONFRONTO FINALE
            st.subheader("🏆 Confronto Finale Accuratezza")
            df_res = pd.DataFrame(results)
            
            fig_bar, ax_bar = plt.subplots(figsize=(10, 5))
            sns.barplot(x="Model", y="Accuracy", data=df_res, palette="viridis", ax=ax_bar)
            ax_bar.set_ylim(0, 1.0)
            for i, row in df_res.iterrows():
                ax_bar.text(float(i), row.Accuracy + 0.01, f"{row.Accuracy:.2f}", color='black', ha="center")
            
            st.pyplot(fig_bar)

    else:
        st.info("Clicca il pulsante sopra per avviare la pipeline di Machine Learning.")