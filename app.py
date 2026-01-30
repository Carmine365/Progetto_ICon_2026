import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.container as mcontainer
import seaborn as sns
import collections.abc
import collections
from sklearn.metrics import roc_curve, auc

# --- FIX COMPATIBILITÀ PYTHON 3.10+ ---
if not hasattr(collections, 'Mapping'): collections.Mapping = collections.abc.Mapping
if not hasattr(collections, 'MutableMapping'): collections.MutableMapping = collections.abc.MutableMapping
if not hasattr(collections, 'Iterable'): collections.Iterable = collections.abc.Iterable

# Import moduli interni
from experta import *
from src.scheduler import laboratoryCsp
from src.bayesian_model import WaterRiskBayesianNetwork
# Manager dell'Ontologia (Single Source of Truth)
from src.ontology_manager import manager 
from src.data_loader import waterData
from src.ml_models import (
    waterLogReg, 
    waterDecTree, 
    waterKnn, 
    waterNeuralNetwork, 
    waterNaiveBayes
)
from src.expert_system import BaseWaterExpert, DEFAULT_PH_MIN, DEFAULT_PH_MAX

# Configurazione pagina
st.set_page_config(page_title="Water Quality AI", layout="wide", page_icon="💧")

# --- CLASSE BRIDGE STREAMLIT-EXPERTA ---
class StreamlitExpert(BaseWaterExpert):
    """Bridge per inviare notifiche Experta alla UI di Streamlit."""
    def notify(self, message, msg_type="info"):
        if msg_type == "error":
            st.error(message)
        elif msg_type == "warning":
            st.warning(message)
        elif msg_type == "success":
            st.success(message)
        else:
            st.info(message)

# --- CACHING DATI & MODELLI ---
@st.cache_data
def load_dataset():
    """Carica il dataset (i NaN sono presenti, gestiti poi dalle Pipeline)."""
    return waterData()

@st.cache_resource
def train_and_evaluate_models(_data):
    """Addestra i modelli una tantum."""
    models = {}
    test_size = 0.2
    
    with st.spinner('Addestramento modelli in corso (Pipeline con Imputer & Scaler)...'):
        # Inizializzazione modelli (che ora contengono le Pipeline)
        models['Logistic Regression'] = waterLogReg(_data, test_size)
        models['Decision Tree'] = waterDecTree(_data, test_size)
        models['KNN'] = waterKnn(_data, test_size)
        models['Neural Network'] = waterNeuralNetwork(_data, test_size)
        models['Naive Bayes'] = waterNaiveBayes(_data, test_size)
        
        # Training effettivo
        for name, model in models.items():
            model.predict() 
            
    return models

# --- MAIN APP ---
def main():
    st.title("💧 Water Quality AI System")
    st.markdown("""
    Piattaforma integrata per l'analisi della potabilità dell'acqua.
    **Moduli:** Machine Learning (Classificazione), Sistema Esperto (Ontologie), Rete Bayesiana (Rischio), CSP (Turni).
    """)

    # ==============================================================================
    # 1. SIDEBAR: INPUT PARAMETRI & MONITORAGGIO SOGLIE
    # ==============================================================================
    st.sidebar.header("🎛️ Pannello di Controllo")
    
    # A. Monitoraggio Soglie Dinamiche (da Ontologia)
    st.sidebar.subheader("📚 Soglie Attive (da OWL)")
    
    # Lettura dinamica tramite il manager
    live_ph_min = manager.get_threshold("AcidicWater", "has_ph_value", DEFAULT_PH_MIN)
    live_ph_max = manager.get_threshold("BasicWater", "has_ph_value", DEFAULT_PH_MAX)
    live_turbidity = manager.get_threshold("TurbidWater", "has_turbidity_value", 5.0)
    live_sulfate = manager.get_threshold("HighSulfateWater", "has_sulfate_value", 250.0)
    
    st.sidebar.info(f"""
    - **pH Range:** {live_ph_min} - {live_ph_max}
    - **Torbidità Max:** {live_turbidity} NTU
    - **Solfati Max:** {live_sulfate} mg/L
    """)

    # B. Input Utente (Tutti i 9 parametri)
    st.sidebar.subheader("🧪 Inserimento Dati Campione")
    with st.sidebar.form("water_input_form"):

        # --- NUOVO: Osservazioni Qualitative ---
        st.markdown("#### 👁️ Osservazioni Preliminari")
        obs_turbidity = st.checkbox("Acqua visivamente torbida?", value=False)
        obs_odor = st.checkbox("Cattivo odore (es. uova marce)?", value=False)
        obs_taste = st.checkbox("Sapore metallico?", value=False)
        st.markdown("---")

        # Parametri Chimico-Fisici Fondamentali
        in_ph = st.slider("pH", 0.0, 14.0, 7.0, help="Acidità/Basicità dell'acqua")
        in_hardness = st.number_input("Durezza (mg/L)", 0.0, 400.0, 200.0)
        in_solids = st.number_input("Solidi Totali (ppm)", 0.0, 50000.0, 20000.0)
        in_chloramines = st.number_input("Cloramine (ppm)", 0.0, 15.0, 7.0)
        in_sulfate = st.number_input("Solfati (mg/L)", 0.0, 500.0, 300.0)
        in_conductivity = st.number_input("Conducibilità (μS/cm)", 0.0, 800.0, 400.0)
        in_organic = st.number_input("Carbonio Organico (ppm)", 0.0, 30.0, 15.0)
        in_thm = st.number_input("Trialometani (μg/L)", 0.0, 150.0, 60.0)
        in_turbidity = st.slider("Torbidità (NTU)", 0.0, 10.0, 4.0)
        
        submit_btn = st.form_submit_button("Analizza Campione")

    # ==============================================================================
    # 2. MAIN TABS
    # ==============================================================================
    tabs = st.tabs([
        "📊 Analisi Dati (EDA)", 
        "🧠 Machine Learning", 
        "🤖 Sistema Esperto", 
        "🔮 Rete Bayesiana", 
        "📅 Gestione Turni"
    ])

    # Caricamento Dati
    data_obj = load_dataset()
    df = data_obj.get_data()

    # --- TAB 1: EDA ---
    with tabs[0]:
        st.header("Analisi Esplorativa dei Dati")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🟢 Distribuzione Potabilità")
            # Grafico Seaborn
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.countplot(x="Potability", data=df, palette="viridis", ax=ax)
            ax.set_title("0 = Non Potabile, 1 = Potabile")
            # Aggiunta etichette
            for container in ax.containers:
                if isinstance(container, mcontainer.BarContainer):
                    ax.bar_label(container)
            st.pyplot(fig)
            
        with col2:
            st.markdown("### 🔥 Matrice di Correlazione")
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(df.corr(numeric_only=True), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
            st.pyplot(fig)

        st.divider()
        st.markdown("### 📈 Analisi Dettagliata pH")
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.histplot(data=df, x="ph", bins=40, kde=True, hue="Potability", palette="coolwarm", element="step", ax=ax)
        # Linee soglia dinamiche
        ax.axvline(live_ph_min, color='red', linestyle='--', label=f'Limite Acido ({live_ph_min})')
        ax.axvline(live_ph_max, color='blue', linestyle='--', label=f'Limite Basico ({live_ph_max})')
        ax.legend()
        st.pyplot(fig)

    # --- TAB 2: MACHINE LEARNING ---
    with tabs[1]:
        st.header("Modelli di Classificazione (Pipeline)")
        st.markdown("I modelli utilizzano una **Pipeline** che gestisce automaticamente i valori mancanti (Imputer) e la normalizzazione (Scaler).")
        
        if st.button("🚀 Avvia Training e Valutazione"):
            models = train_and_evaluate_models(data_obj)
            results_stats = []
            
            for name, model in models.items():
                st.subheader(f"🔹 {name}")
                c1, c2, c3 = st.columns([1, 1, 1])
                
                # 1. Metriche Numeriche
                scores = model.get_metric()
                results_stats.append({"Model": name, "Accuracy": scores['Accuracy']})
                with c1:
                    st.write("**Performance:**")
                    st.json(scores)
                
                # 2. Confusion Matrix
                # ... dentro il ciclo for dei modelli ...
                # 2. Confusion Matrix
                with c2:
                    st.write("**Matrice di Confusione:**")
                    try:
                        cm = model.get_confusion_matrix() # Ora restituisce la matrice!
                        
                        if cm is not None:
                            fig_cm, ax_cm = plt.subplots(figsize=(3, 3))
                            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False, ax=ax_cm)
                            ax_cm.set_xlabel('Predicted')
                            ax_cm.set_ylabel('Actual')
                            st.pyplot(fig_cm)
                        else:
                            st.warning("Dati non pronti (cm is None)")
                    except Exception as e: 
                        st.warning(f"Errore: {e}")
                            
                    except Exception as e:
                        # Stampa l'errore vero invece di "N/D"
                        st.error(f"Errore plot: {e}")

                # 3. Curva ROC
                with c3:
                    st.write("**Curva ROC:**")
                    try:
                        # Estrazione dell'estimator dalla Pipeline (ultimo step)
                        estimator = model.model.steps[-1][1] if hasattr(model.model, 'steps') else model.model
                        
                        if hasattr(estimator, "predict_proba"):
                            y_probs = model.model.predict_proba(model.x_test)[:, 1]
                            fpr, tpr, _ = roc_curve(model.y_test, y_probs)
                            roc_auc = auc(fpr, tpr)
                            
                            fig_roc, ax_roc = plt.subplots(figsize=(3, 3))
                            ax_roc.plot(fpr, tpr, color='darkorange', lw=2, label=f'AUC = {roc_auc:.2f}')
                            ax_roc.plot([0, 1], [0, 1], color='navy', linestyle='--')
                            ax_roc.legend(loc="lower right")
                            st.pyplot(fig_roc)
                        else:
                            st.info("ROC non disponibile (no predict_proba).")
                    except Exception as e:
                        st.error(f"Errore ROC: {e}")
                
                st.divider()

            # Confronto Finale
            st.subheader("🏆 Classifica Accuratezza")
            df_res = pd.DataFrame(results_stats).sort_values(by="Accuracy", ascending=False)
            
            if not df_res.empty:
                fig_bar, ax_bar = plt.subplots(figsize=(10, 5))
                sns.barplot(x="Model", y="Accuracy", data=df_res, palette="magma", ax=ax_bar)
                ax_bar.set_ylim(0, 1.0)
                # Etichette sulle barre
                for container in ax_bar.containers:
                    if isinstance(container, mcontainer.BarContainer):
                        ax_bar.bar_label(container, fmt='%.2f', padding=3)
                st.pyplot(fig_bar)

    # --- TAB 3: SISTEMA ESPERTO (IBRIDO) ---
    with tabs[2]:
        st.header("🕵️ Diagnostica Basata su Regole")
        st.info("Il sistema analizza i dati inseriti nella Sidebar confrontandoli con l'Ontologia OWL.")
        
        if submit_btn:
            # Istanziazione Engine collegato a Streamlit
            engine = StreamlitExpert()
            engine.reset()
            
            # Caricamento Fatti (Tutti i 9 parametri)
            engine.declare(Fact(param='ph', value=in_ph))
            engine.declare(Fact(param='hardness', value=in_hardness))
            engine.declare(Fact(param='solids', value=in_solids))
            engine.declare(Fact(param='chloramines', value=in_chloramines))
            engine.declare(Fact(param='sulfate', value=in_sulfate))
            engine.declare(Fact(param='conductivity', value=in_conductivity))
            engine.declare(Fact(param='organic_carbon', value=in_organic))
            engine.declare(Fact(param='trihalomethanes', value=in_thm))
            engine.declare(Fact(param='turbidity', value=in_turbidity))

            # --- NUOVO: Passaggio osservazioni qualitative ---
            if obs_turbidity:
                engine.declare(Fact(osservazione_torbida="si"))
            if obs_odor:
                engine.declare(Fact(osservazione_odore="si"))
            if obs_taste:
                engine.declare(Fact(osservazione_sapore="si"))
            
            # Esecuzione
            st.markdown("### 📝 Report Analisi")
            engine.run()
            
            # Riepilogo Problemi
            if engine.problems_count > 0:
                st.error(f"🔴 Rilevate {engine.problems_count} anomalie critiche!")
                if engine.csp_suggestion:
                    st.warning(f"💡 Azione Richiesta: Necessario intervento '{engine.csp_suggestion}'. Vai al tab 'Gestione Turni'.")
            else:
                st.success("✅ Tutti i parametri rientrano nelle soglie di sicurezza WHO/Ontologia.")
        else:
            st.write("👈 Inserisci i dati nella Sidebar e clicca 'Analizza Campione'.")

    # --- TAB 4: RETE BAYESIANA ---
    with tabs[3]:
        with tabs[3]:
            st.header("🕸️ Analisi Probabilistica del Rischio")
            st.markdown("Stima il rischio ambientale basandosi su osservazioni qualitative (non numeriche).")
            
            # 1. INPUT CONFORMI A bayesian_model.py
            c1, c2 = st.columns(2)
            with c1:
                has_industry = st.checkbox("🏭 Vicinanza Industrie?", value=False)
                heavy_rain = st.checkbox("⛈️ Piogge Intense Recenti?", value=False)
            with c2:
                odore = st.checkbox("👃 Odore Sospetto?", value=False)
                sapore = st.checkbox("👅 Sapore Metallico?", value=False)
                vista = st.checkbox("👁️ Acqua Torbida alla vista?", value=False)
            
            if st.button("🔮 Calcola Rischio (Bayes)"):
                bn = WaterRiskBayesianNetwork()
                try:
                    # CHIAMATA CORRETTA AL METODO ESISTENTE
                    risk_prob = bn.get_risk_probability(
                        has_industry=has_industry,
                        heavy_rain=heavy_rain,
                        odore_presente=odore,
                        taste=sapore,
                        visual=vista
                    )
                    
                    # Visualizzazione
                    st.metric(label="Probabilità di Inquinamento (Rischio)", value=f"{risk_prob*100:.1f}%")
                    
                    if risk_prob > 0.6:
                        st.error("🚨 RISCHIO ALTO: Si consiglia di non consumare l'acqua.")
                    elif risk_prob > 0.3:
                        st.warning("⚠️ RISCHIO MODERATO: Richieste analisi di laboratorio.")
                    else:
                        st.success("✅ RISCHIO BASSO: Probabilmente sicura (ma verifica i parametri chimici).")
                        
                except Exception as e:
                    st.error(f"Errore nel calcolo Bayesiano: {e}")

    # --- TAB 5: SCHEDULER CSP ---
    with tabs[4]:
        st.header("📅 Ottimizzazione Turni Laboratorio")
        st.markdown("Algoritmo CSP (Constraint Satisfaction Problem) per assegnare lo staff in base al tipo di emergenza.")
        
        issue_type = st.selectbox("Seleziona Scenario Operativo:", 
                                  ["general", "chemical", "physical", "critical"])
        
        if st.button("🧩 Genera Turni"):
            csp = laboratoryCsp(issue_type)
            solutions = csp.get_solutions_list()
            
            if not solutions:
                st.error("Nessuna soluzione trovata.")
            elif "NESSUN TURNO" in solutions[0]:
                st.error(solutions[0])
            else:
                st.success(f"Trovate {len(solutions)} combinazioni valide.")
                for i, sol in enumerate(solutions):
                    st.info(f"Opzione {i+1}: {sol}")

if __name__ == "__main__":
    main()