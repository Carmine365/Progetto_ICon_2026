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

# --- COSTANTI WHO ---
PH_MIN = 6.5
PH_MAX = 8.5
TURBIDITY_MAX = 5.0
SOLIDS_MAX = 1000
HARDNESS_LIMIT = 300

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

    def notify(self, message, msg_type="info"):
        """Metodo da sovrascrivere nelle sottoclassi (CLI o GUI)"""
        pass

    @DefFacts()
    def _initial_action(self):
        yield Fact(inizio="si")

    # --- REGOLE DI DIAGNOSI (Condivise) ---

    @Rule(Fact(param='ph', value=MATCH.val))
    def check_ph(self, val):
        if val < PH_MIN:
            self.notify(f"🔴 pH ACIDO rilevato ({val}). Corrosivo!", "error")
            self.declare(Fact(problema_ph="acido"))
            self.problems_count += 1
        elif val > PH_MAX:
            self.notify(f"🔴 pH BASICO rilevato ({val}).", "error")
            self.declare(Fact(problema_ph="basico"))
            self.problems_count += 1
        else:
            self.notify(f"✅ pH nella norma ({val}).", "success")

    @Rule(Fact(param='sulfate', value=MATCH.val))
    def check_sulfate(self, val):
        if val > 250:
            self.notify(f"⚠️ Solfati ALTI ({val} mg/L).", "warning")
            self.declare(Fact(problema_solfati="alto"))
            self.problems_count += 1
        else:
            self.notify("✅ Solfati nella norma.", "success")

    @Rule(Fact(param='turbidity', value=MATCH.val))
    def check_turbidity(self, val):
        if val > TURBIDITY_MAX:
            self.notify(f"🔴 Torbidità ALTA ({val} NTU). Acqua sporca.", "error")
            self.declare(Fact(problema_torbidita="alta"))
            self.problems_count += 1
        else:
            self.notify("✅ Torbidità nella norma.", "success")

    @Rule(Fact(param='solids', value=MATCH.val))
    def check_solids(self, val):
        if val > SOLIDS_MAX:
            self.notify(f"🔴 TDS Alto ({val} ppm). Acqua troppo mineralizzata.", "error")
            self.declare(Fact(problema_solidi="alto"))
            self.problems_count += 1

    @Rule(Fact(param='hardness', value=MATCH.val))
    def check_hardness(self, val):
        if val > HARDNESS_LIMIT:
            self.notify(f"ℹ️ Acqua dura ({val} mg/L). Possibili incrostazioni.", "info")

    # --- REGOLA RELAZIONALE COMPLESSA ---
    @Rule(Fact(param='ph', value=P(lambda x: x < 6.0)),
          Fact(param='sulfate', value=P(lambda x: x > 200)))
    def corrosion_risk(self):
        self.notify("🔥 COMBINAZIONE CRITICA: pH Acido + Solfati Alti! Rischio corrosione.", "error")
        self.declare(Fact(problem_type="critical"))
        self.csp_suggestion = "critical"

    # --- INFERENZA NECESSITÀ INTERVENTO ---
    @Rule(OR(Fact(problema_ph="acido"), Fact(problema_ph="basico"), Fact(problema_solfati="alto")))
    def infer_chemical_need(self):
        if self.csp_suggestion != "critical":
            self.csp_suggestion = "chemical"
            self.declare(Fact(need_lab="chemical"))

    @Rule(OR(Fact(problema_torbidita="alta"), Fact(problema_solidi="alto")))
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
        self.mean_water_values = water_data().get_medium_values_water()
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
            csp = laboratory_csp(issue_type=issue_type)
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
        self.declare(Fact(step="ask_ph"))

    @Rule(Fact(step="ask_ph"))
    def ask_ph(self):
        print("\nInserisci pH (0-14):")
        try:
            val = float(input())
            if valid_ph(val):
                # DICHIARIAMO IL FATTO: La classe Base scatterà automaticamente per controllarlo!
                self.declare(Fact(param='ph', value=val))
            else:
                print("Valore fuori range.")
        except ValueError:
            print("Inserimento saltato.")
        self.declare(Fact(step="ask_sulfates"))

    @Rule(Fact(step="ask_sulfates"))
    def ask_sulfates(self):
        print("\nInserisci Solfati (mg/L):")
        try:
            val = float(input())
            self.declare(Fact(param='sulfate', value=val))
        except ValueError: pass
        self.declare(Fact(step="ask_turbidity"))

    @Rule(Fact(step="ask_turbidity"))
    def ask_turbidity(self):
        print("\nInserisci Torbidità (NTU):")
        try:
            val = float(input())
            self.declare(Fact(param='turbidity', value=val))
        except ValueError: pass
        self.declare(Fact(step="ask_solids"))
        
    @Rule(Fact(step="ask_solids"))
    def ask_solids(self):
        print("\nInserisci Solidi TDS (ppm):")
        try:
            val = float(input())
            self.declare(Fact(param='solids', value=val))
        except ValueError: pass
        self.declare(Fact(step="ask_hardness"))

    @Rule(Fact(step="ask_hardness"))
    def ask_hardness(self):
        print("\nInserisci Durezza (mg/L):")
        try:
            val = float(input())
            self.declare(Fact(param='hardness', value=val))
        except ValueError: pass
        self.declare(Fact(fine_analisi="si"))

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