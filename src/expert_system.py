import collections.abc
import collections
# FIX COMPATIBILITÀ PYTHON 3.10+
if not hasattr(collections, 'Mapping'): collections.Mapping = collections.abc.Mapping
if not hasattr(collections, 'MutableMapping'): collections.MutableMapping = collections.abc.MutableMapping
if not hasattr(collections, 'Iterable'): collections.Iterable = collections.abc.Iterable

from experta import *
from colorama import Fore, Style, init
from .data_loader import waterData
from .scheduler import laboratoryCsp
from .ontology_manager import manager # Importiamo l'istanza del manager

# --- COSTANTI WHO (DEFAULT / FALLBACK) ---
# Usate se l'ontologia non risponde o la classe non esiste
DEFAULT_PH_MIN = 6.5
DEFAULT_PH_MAX = 8.5
DEFAULT_TURBIDITY_MAX = 5.0
DEFAULT_SULFATE_MAX = 250.0       
DEFAULT_SOLIDS_MAX = 1000.0
DEFAULT_HARDNESS_LIMIT = 300.0
DEFAULT_CHLORAMINES_MAX = 4.0     # mg/L
DEFAULT_CONDUCTIVITY_MAX = 800.0  # uS/cm
DEFAULT_ORGANIC_CARBON_MAX = 10.0 # ppm 
DEFAULT_THM_MAX = 80.0            # ug/L

def valid_response(response: str):
    return response.lower().strip() in ["si", "no"]

def valid_ph(ph: float):
    return 0 <= ph <= 14

# ==============================================================================
# CLASSE BASE (LOGICA CONDIVISA)
# ==============================================================================
class BaseWaterExpert(KnowledgeEngine):
    """
    Contiene TUTTA la logica diagnostica. 
    Non fa print() né input(), ma delega l'output al metodo notify().
    """
    def __init__(self):
        super().__init__()
        self.problems_count = 0
        self.csp_suggestion = None # 'chemical', 'physical', 'critical'

        # --- CARICAMENTO IBRIDO (Ontologia con Fallback) ---
        # Il sistema cerca la soglia nell'Ontologia. Se fallisce, usa il DEFAULT.
        
        # 1. pH (Acido e Basico)
        self.PH_MIN = manager.get_threshold("AcidicWater", "has_ph_value", DEFAULT_PH_MIN)
        self.PH_MAX = manager.get_threshold("BasicWater", "has_ph_value", DEFAULT_PH_MAX)
        
        # 2. Parametri Fisici
        self.TURBIDITY_MAX = manager.get_threshold("TurbidWater", "has_turbidity_value", DEFAULT_TURBIDITY_MAX)
        self.SOLIDS_MAX = manager.get_threshold("HighSolidsWater", "has_solids_value", DEFAULT_SOLIDS_MAX)
        self.CONDUCTIVITY_MAX = manager.get_threshold("HighConductivityWater", "has_conductivity_value", DEFAULT_CONDUCTIVITY_MAX)

        # 3. Parametri Chimici
        self.SULFATE_MAX = manager.get_threshold("HighSulfateWater", "has_sulfate_value", DEFAULT_SULFATE_MAX)
        self.CHLORAMINES_MAX = manager.get_threshold("HighChloraminesWater", "has_chloramines_value", DEFAULT_CHLORAMINES_MAX)
        self.HARDNESS_LIMIT = manager.get_threshold("HardWater", "has_hardness_value", DEFAULT_HARDNESS_LIMIT)

        # 4. Parametri Tossici/Biologici
        self.ORGANIC_CARBON_MAX = manager.get_threshold("HighCarbonWater", "has_organic_carbon_value", DEFAULT_ORGANIC_CARBON_MAX)
        self.THM_MAX = manager.get_threshold("HighTHMWater", "has_trihalomethanes_value", DEFAULT_THM_MAX)
        
        # Debug per verificare cosa ha caricato (utile per l'esame)
        print(f"\n[SISTEMA IBRIDO] Soglie Caricate:")
        print(f"   -> pH Range: {self.PH_MIN} - {self.PH_MAX}")
        print(f"   -> Solfati Max: {self.SULFATE_MAX}")
        print(f"   -> Torbidità Max: {self.TURBIDITY_MAX}")
        
    def notify(self, message, msg_type="info"):
        """Metodo da sovrascrivere nelle sottoclassi (CLI o GUI)"""
        pass

    @DefFacts()
    def _initial_action(self):
        yield Fact(inizio="si")

    # --- REGOLE DI DIAGNOSI (Condivise) ---

    @Rule(Fact(param='ph', value=MATCH.val))
    def check_ph(self, val):
        if val < self.PH_MIN:
            self.notify(f"🔴 pH ACIDO rilevato (< {self.PH_MIN}). Corrosivo!", "error")
            self.declare(Fact(problema_ph="acido"))
            self.problems_count += 1
        elif val > self.PH_MAX:
            self.notify(f"🔴 pH BASICO rilevato (> {self.PH_MAX}).", "error")
            self.declare(Fact(problema_ph="basico"))
            self.problems_count += 1
        else:
            self.notify(f"✅ pH nella norma ({val}).", "success")

    @Rule(Fact(param='sulfate', value=MATCH.val))
    def check_sulfate(self, val):
        if val > self.SULFATE_MAX: # Dinamico
            self.notify(f"⚠️ Solfati ALTI ({val} mg/L).", "warning")
            self.declare(Fact(problema_solfati="alto"))
            self.problems_count += 1
        else:
            self.notify("✅ Solfati nella norma.", "success")

    @Rule(Fact(param='turbidity', value=MATCH.val))
    def check_turbidity(self, val):
        if val > self.TURBIDITY_MAX:
            self.notify(f"🔴 Torbidità ALTA ({val} NTU). Acqua sporca.", "error")
            self.declare(Fact(problema_torbidita="alta"))
            self.problems_count += 1
        else:
            self.notify("✅ Torbidità nella norma.", "success")

    @Rule(Fact(param='solids', value=MATCH.val))
    def check_solids(self, val):
        if val > self.SOLIDS_MAX:
            self.notify(f"🔴 TDS Alto ({val} ppm). Acqua troppo mineralizzata.", "error")
            self.declare(Fact(problema_solidi="alto"))
            self.problems_count += 1

    @Rule(Fact(param='hardness', value=MATCH.val))
    def check_hardness(self, val):
        if val > self.HARDNESS_LIMIT:
            self.notify(f"ℹ️ Acqua dura ({val} mg/L). Possibili incrostazioni.", "info")

    @Rule(Fact(param='chloramines', value=MATCH.val))
    def check_chloramines(self, val):
        if val > self.CHLORAMINES_MAX:
            self.notify(f"⚠️ Cloramine ALTE ({val} ppm). Sapore sgradevole/Rischio.", "warning")
            self.declare(Fact(problema_chimico="cloramine"))
            self.problems_count += 1

    @Rule(Fact(param='conductivity', value=MATCH.val))
    def check_conductivity(self, val):
        if val > self.CONDUCTIVITY_MAX:
            self.notify(f"ℹ️ Conducibilità alta ({val}). Presenza di ioni disciolti.", "info")

    @Rule(Fact(param='organic_carbon', value=MATCH.val))
    def check_organic_carbon(self, val):
        if val > self.ORGANIC_CARBON_MAX:
            self.notify(f"🔴 Carbonio Organico Alto ({val} ppm). Rischio biologico.", "error")
            self.declare(Fact(problema_biologico="carbonio"))
            self.problems_count += 1

    @Rule(Fact(param='trihalomethanes', value=MATCH.val))
    def check_trihalomethanes(self, val):
        if val > self.THM_MAX:
            self.notify(f"🔴 Trialometani PERICOLOSI ({val} ug/L). Cancerogeni.", "error")
            self.declare(Fact(problema_tossico="thm"))
            self.problems_count += 1

    # --- REGOLA RELAZIONALE COMPLESSA ---
    @Rule(Fact(param='ph', value=P(lambda x: x < 6.0)),
          Fact(param='sulfate', value=P(lambda x: x > 200)))
    def corrosion_risk(self):
        self.notify("🔥 COMBINAZIONE CRITICA: pH Acido + Solfati Alti! Rischio corrosione.", "error")
        self.declare(Fact(problem_type="critical"))
        self.csp_suggestion = "critical"

    # --- INFERENZA INTERVENTO (Aggiornata) ---
    @Rule(OR(Fact(problema_ph=W()), Fact(problema_solfati=W()), Fact(problema_chimico=W()), Fact(problema_tossico=W())))
    def infer_chemical_need(self):
        if self.csp_suggestion != "critical":
            self.csp_suggestion = "chemical"
            self.declare(Fact(need_lab="chemical"))

    @Rule(OR(Fact(problema_fisico=W()), Fact(problema_biologico=W())))
    def infer_physical_need(self):
        if self.csp_suggestion != "critical":
            self.csp_suggestion = "physical"
            self.declare(Fact(need_lab="physical"))


# ==============================================================================
# VERSIONE CLI (INTERATTIVA)
# ==============================================================================
class WaterExpert(BaseWaterExpert):
    """
    Estende la base aggiungendo l'interazione via Terminale (input/print).
    """
    @DefFacts()
    def _load_data(self):
        # Carica le medie solo per la CLI se servono
        self.mean_water_values = waterData().get_medium_values_water()
        yield Fact(mode="cli")

    def notify(self, message, msg_type="info"):
        if msg_type == "error":
            print(Fore.RED + message + Fore.RESET)
        elif msg_type == "warning":
            print(Fore.YELLOW + message + Fore.RESET)
        elif msg_type == "success":
            print(Fore.GREEN + message + Fore.RESET)
        else:
            print(Fore.CYAN + message + Fore.RESET)

    def _run_scheduler_cli(self, issue_type):
        print(Fore.MAGENTA + f"\n[CSP] Ricerca turno per: {issue_type.upper()}..." + Fore.RESET)
        try:
            csp = laboratoryCsp(issue_type=issue_type)
            solutions = csp.get_solutions_list()
            if solutions:
                print(f"   >> Turno Assegnato: {solutions[0]}")
            else:
                print(Fore.RED + "   >> NESSUN TURNO DISPONIBILE." + Fore.RESET)
        except Exception as e:
            print(f"Errore Scheduler: {e}")

    # --- REGOLE DI INTERAZIONE (Domanda -> Risposta) ---

    @Rule(Fact(inizio="si"), Fact(mode="cli"))
    def start_diagnosis(self):
        print(Fore.CYAN + "\n=== AVVIO SISTEMA ESPERTO (CLI) ===\n" + Fore.RESET)
        self.declare(Fact(step="ask_observations"))

    # --- NUOVA FASE: OSSERVAZIONALE ---
    @Rule(Fact(step="ask_observations"))
    def ask_observations(self):
        print(Fore.YELLOW + "--- FASE 1: OSSERVAZIONE VISIVA ---" + Fore.RESET)
        
        # Domanda 1: Torbidità visiva
        ans = input("L'acqua appare torbida o nuvolosa? [si/no]: ").lower()
        if ans == "si":
            self.declare(Fact(osservazione_torbida="si"))
        
        # Domanda 2: Odore
        ans = input("L'acqua ha un cattivo odore (es. uova marce, cloro)? [si/no]: ").lower()
        if ans == "si":
            self.declare(Fact(osservazione_odore="si"))
            print(Fore.YELLOW + " >> Nota: Possibile contaminazione batterica o eccesso di cloro." + Fore.RESET)

        # Domanda 3: Sapore
        ans = input("L'acqua ha un sapore metallico? [si/no]: ").lower()
        if ans == "si":
            self.declare(Fact(osservazione_sapore="si"))

        print(Fore.GREEN + "Osservazioni registrate. Procediamo con l'analisi strumentale.\n" + Fore.RESET)
        self.declare(Fact(step="ask_ph"))

    # --- FASE STRUMENTALE (Aggiornata) ---

    @Rule(Fact(step="ask_ph"))
    def ask_ph(self):
        print("[1/9] Inserisci pH (0-14):")
        try:
            val = float(input())
            if valid_ph(val):
                self.declare(Fact(param='ph', value=val))
            else:
                print("Valore fuori range.")
        except ValueError:
            print("Inserimento saltato.")
        self.declare(Fact(step="ask_sulfates"))

    @Rule(Fact(step="ask_sulfates"))
    def ask_sulfates(self):
        print("\n[2/9] Inserisci Solfati (mg/L):")
        try:
            val = float(input())
            self.declare(Fact(param='sulfate', value=val))
        except ValueError: pass
        self.declare(Fact(step="ask_turbidity"))

    @Rule(Fact(step="ask_turbidity"))
    def ask_turbidity(self):
        print("\n[3/9] Inserisci Torbidità (NTU):")
        
        # INTEGRAZIONE: Se l'utente aveva visto acqua torbida, ricordaglielo
        if self.facts.get(Fact(osservazione_torbida="si")):
            print(Fore.YELLOW + "⚠️  NOTA: Avevi segnalato visivamente acqua torbida." + Fore.RESET)
        
        try:
            val = float(input())
            self.declare(Fact(param='turbidity', value=val))
        except ValueError: pass
        self.declare(Fact(step="ask_solids"))
        
    @Rule(Fact(step="ask_solids"))
    def ask_solids(self):
        print("\n[4/9] Inserisci Solidi TDS (ppm):")
        try:
            val = float(input())
            self.declare(Fact(param='solids', value=val))
        except ValueError: pass
        self.declare(Fact(step="ask_hardness"))

    @Rule(Fact(step="ask_hardness"))
    def ask_hardness(self):
        print("\n[5/9] Inserisci Durezza (mg/L):")
        try:
            val = float(input())
            self.declare(Fact(param='hardness', value=val))
        except ValueError: pass
        self.declare(Fact(step="ask_chloramines"))

    # 6. Cloramine
    @Rule(Fact(step="ask_chloramines"))
    def ask_chloramines(self):
        print("\n[6/9] Inserisci Cloramine (ppm):")
        try:
            self.declare(Fact(param='chloramines', value=float(input())))
        except ValueError: pass
        self.declare(Fact(step="ask_conductivity"))

    # 7. Conducibilità
    @Rule(Fact(step="ask_conductivity"))
    def ask_conductivity(self):
        print("\n[7/9] Inserisci Conducibilità (uS/cm):")
        try:
            self.declare(Fact(param='conductivity', value=float(input())))
        except ValueError: pass
        self.declare(Fact(step="ask_organic"))

    # 8. Carbonio Organico
    @Rule(Fact(step="ask_organic"))
    def ask_organic(self):
        print("\n[8/9] Inserisci Carbonio Organico (ppm):")
        try:
            self.declare(Fact(param='organic_carbon', value=float(input())))
        except ValueError: pass
        self.declare(Fact(step="ask_thm"))

    # 9. Trialometani
    @Rule(Fact(step="ask_thm"))
    def ask_thm(self):
        print("\n[9/9] Inserisci Trialometani (ug/L):")
        try:
            self.declare(Fact(param='trihalomethanes', value=float(input())))
        except ValueError: pass
        self.declare(Fact(fine_analisi="si")) # FINE

    # --- REAZIONE AGLI ALLERTI (CLI Specifico) ---
    @Rule(Fact(need_lab=MATCH.type))
    def trigger_scheduler(self, type):
        self._run_scheduler_cli(type)
    
    @Rule(Fact(problem_type="critical"))
    def trigger_critical(self):
        self._run_scheduler_cli("critical")

    @Rule(Fact(fine_analisi="si"))
    def final_report(self):
        print("\n=== REPORT FINALE ===")
        if self.problems_count == 0:
            print(Fore.GREEN + "Acqua POTABILE." + Fore.RESET)
        else:
            print(Fore.RED + f"Acqua NON SICURA. Rilevate {self.problems_count} anomalie." + Fore.RESET)