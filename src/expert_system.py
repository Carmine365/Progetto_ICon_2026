import collections.abc
# --- FIX PER PYTHON 3.10+ ---
import collections
# "Inganniamo" la libreria experta ripristinando i vecchi riferimenti
if not hasattr(collections, 'Mapping'):
    collections.Mapping = collections.abc.Mapping
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping
if not hasattr(collections, 'Iterable'):
    collections.Iterable = collections.abc.Iterable
# ----------------------------

from experta import *
from colorama import Fore, Style, init
from .data_loader import water_data
from .scheduler import laboratory_csp
from .ontology_manager import water_ontology

# --- COSTANTI WHO (World Health Organization) ---
PH_MIN = 6.5
PH_MAX = 8.5
TURBIDITY_MAX = 5.0
SOLIDS_MAX = 1000  # mg/L
HARDNESS_LIMIT = 300 # Esempio soglia attenzione

def reset_color():
    print(Fore.RESET)

def valid_response(response: str):
    response = response.lower().strip()
    return response == "si" or response == "no"

def valid_ph(ph: float):
    return 0 <= ph <= 14

class WaterExpert(KnowledgeEngine):

    @DefFacts()
    def _initial_action(self):
        yield Fact(inizio="si")
        # Carica le medie dal dataset (usato per confrontare i valori utente)
        self.mean_water_values = water_data().get_medium_values_water()
        self.problems_found = 0

        # --- DEFINIZIONE TURNI LABORATORI (CSP) ---
        # 1. Laboratorio Chimico (per pH, Cloramina)
        self.lab_chemical = laboratory_csp("Laboratorio Analisi Chimiche")
        self.lab_chemical.addConstraint(lambda day, hours: hours >= 8 and hours <= 14 if day == "lunedi" else hours >= 15 and hours <= 19 if day == "giovedi" else None, ["day", "hours"])

        # 2. Laboratorio Fisico (per Torbidità, Solidi)
        self.lab_physical = laboratory_csp("Laboratorio Analisi Fisiche")
        self.lab_physical.addConstraint(lambda day, hours: hours >= 9 and hours <= 13 if day == "martedi" else hours >= 14 and hours <= 18 if day == "venerdi" else None, ["day", "hours"])

        # 3. Laboratorio Depurazione (per trattamenti correttivi)
        self.lab_treatment = laboratory_csp("Impianto di Depurazione")
        self.lab_treatment.addConstraint(lambda day, hours: hours >= 8 and hours <= 16 if day == "mercoledi" else hours >= 8 and hours <= 12 if day == "sabato" else None, ["day", "hours"])

    def print_facts(self):
        print("\n\n[DEBUG] L'agente ragiona con i seguenti fatti attivi: \n")
        print(self.facts)

    def _prototype_lab_booking(self, ask_text: str, lab_selected: laboratory_csp):
        print(Fore.YELLOW + f"\n[SUGGERIMENTO] Visti i valori anomali di {ask_text}, vuoi prenotare un intervento tecnico? [si/no]" + Fore.RESET)
        response = str(input()).lower()

        while not valid_response(response):
            print("Rispondi 'si' o 'no'")
            response = str(input()).lower()
        
        if response == "si":
            first, last = lab_selected.get_availability()
            print(f"Inserisci un turno disponibile (da {first} a {last}):")
            
            try:
                turn_input = int(input())
                while turn_input < first or turn_input > last:
                    print(f"Turno non valido. Inserisci un numero tra {first} e {last}")
                    turn_input = int(input())
                
                lab_selected.print_single_availability(turn_input)
            except ValueError:
                print("Inserimento annullato (non hai inserito un numero).")

    def _prototype_ask_observation(self, ask_text: str, fact_declared: Fact):
        print(ask_text)
        response = str(input()).lower()
        while not valid_response(response):
            print("Rispondi 'si' o 'no'")
            response = str(input()).lower()
        
        if response == "si":
            self.declare(fact_declared)
        return response

    # --- REGOLE DEL SISTEMA ESPERTO ---

    @Rule(Fact(inizio="si"))
    def start_diagnosis(self):
        print(Fore.CYAN + "\n=== AVVIO SISTEMA ESPERTO QUALITÀ ACQUA ===\n")
        reset_color()
        self.declare(Fact(chiedi_osservazioni="si"))

    # 1. FASE OSSERVAZIONALE
    @Rule(Fact(chiedi_osservazioni="si"))
    def ask_observations(self):
        print("Rispondi alle domande sull'aspetto del campione d'acqua:\n")
        
        self._prototype_ask_observation("L'acqua appare torbida o nuvolosa? [si/no]", Fact(acqua_torbida="si"))
        self._prototype_ask_observation("L'acqua ha un cattivo odore (es. uova marce, cloro)? [si/no]", Fact(cattivo_odore="si"))
        self._prototype_ask_observation("L'acqua ha un sapore metallico o amaro? [si/no]", Fact(sapore_strano="si"))
        self._prototype_ask_observation("Hai notato residui o sedimenti sul fondo? [si/no]", Fact(sedimenti="si"))

        # 1. Attiviamo il flag che abilita le regole relazionali complesse
        self.declare(Fact(action="analyze"))  
        
        # 2. Passiamo alla fase successiva
        self.declare(Fact(fase_analisi_strumentale="si"))

    # --- NUOVA REGOLA RELAZIONALE ---
    @Rule(
        Fact(action="analyze"),
        Fact(param='ph', value=P(lambda x: x < 6.0)),      # pH Acido
        Fact(param='sulfate', value=P(lambda x: x > 200))  # Solfati Alti
    )
    def corrosion_risk_alert(self):
        print(Fore.RED + "\n!!! ALLARME RELAZIONALE ATTIVATO !!!")
        print("   >> Combinazione Critica: pH Acido + Solfati Alti")
        print("   >> Rischio immediato corrosione tubature." + Fore.RESET)
        
        self.declare(Fact(problem_type="critical"))

    # 2. FASE ANALISI STRUMENTALE (Ex Esami Sangue)
    @Rule(Fact(fase_analisi_strumentale="si"))
    def ask_ph(self):
        print(Fore.CYAN + "\n--- ANALISI CHIMICA (pH) ---")
        reset_color()
        print("Inserisci il valore del pH rilevato (0-14):")
        try:
            ph_val = float(input())
            while not valid_ph(ph_val):
                print("Valore non valido. Inserisci un numero tra 0 e 14:")
                ph_val = float(input())
            
            # --- MODIFICA FONDAMENTALE ---
            # Dichiariamo il fatto numerico che serve alla regola "Corrosion Risk"
            # Senza questa riga, la regola relazionale non saprà mai quanto vale il pH!
            self.declare(Fact(param='ph', value=ph_val)) 
            # -----------------------------

            if ph_val < PH_MIN:
                print(Fore.RED + f"ALLARME: pH ACIDO ({ph_val}). Corrosivo per le tubature.")
                reset_color()
                self.declare(Fact(problema_ph="acido"))
                self.problems_found += 1
            elif ph_val > PH_MAX:
                print(Fore.RED + f"ALLARME: pH BASICO ({ph_val}).")
                reset_color()
                self.declare(Fact(problema_ph="basico"))
                self.problems_found += 1
            else:
                print(Fore.GREEN + "pH nella norma.")
                reset_color()
                self.declare(Fact(ph_ok="si"))
        except ValueError:
            print("Valore non numerico inserito, salto questo test.")

        self.declare(Fact(step="ask_sulfates"))

    # --- 2. DOMANDA SOLFATI (Quella che ti mancava) ---
    @Rule(Fact(step="ask_sulfates"))
    def ask_sulfates(self):
        print(Fore.CYAN + "\n--- ANALISI SOLFATI ---" + Fore.RESET)
        try:
            # Chiede input
            val = float(input("Inserisci concentrazione Solfati (mg/L): "))
            
            # 1. Dichiara il FATTO NUMERICO (Il secondo pezzo del puzzle!)
            self.declare(Fact(param='sulfate', value=val))
            
            # 2. Feedback immediato
            if val > 250:
                print(Fore.YELLOW + f" >> ATTENZIONE: Solfati alti ({val} mg/L)." + Fore.RESET)
                self.declare(Fact(problema_solfati="alto"))
            else:
                print(Fore.GREEN + " >> Solfati nella norma." + Fore.RESET)
            
            # 3. Passa allo step successivo (es. Torbidità o Fine)
            self.declare(Fact(step="ask_turbidity")) 
            
        except ValueError:
            print("Valore non valido.")
            self.declare(Fact(step="ask_turbidity"))

    # 3. ANALISI TORBIDITÀ (Sostituisce Glicemia Casuale)
    @Rule(Fact(step="ask_turbidity"))
    def ask_turbidity(self):
        print(Fore.CYAN + "\n--- ANALISI FISICA (Torbidità) ---")
        reset_color()
        
        # Se l'utente aveva detto che l'acqua era torbida visivamente, lo ricordiamo
        if self.facts.get(Fact(acqua_torbida="si")):
            print(Fore.YELLOW + "Nota: Avevi segnalato visivamente acqua torbida.")
            reset_color()

        print("Inserisci il valore di Torbidità (NTU):")
        try:
            turb_val = float(input())
            if turb_val > TURBIDITY_MAX:
                self.declare(Fact(problema_torbidita="alta"))
                self.problems_found += 1
            else:
                self.declare(Fact(torbidita_ok="si"))
        except ValueError: pass
        
        self.declare(Fact(chiedi_solidi="si"))

    # 4. ANALISI SOLIDI E DUREZZA (Sostituisce BMI e Pressione)
    @Rule(Fact(chiedi_solidi="si"))
    def ask_solids_hardness(self):
        print(Fore.CYAN + "\n--- ANALISI SOLIDI E DUREZZA ---")
        reset_color()
        
        # SOLIDI (TDS)
        print("Inserisci i Solidi Totali Disciolti (TDS) in ppm:")
        try:
            tds = float(input())
            avg_tds = self.mean_water_values.get('Solids', 22000) # Fallback se vuoto
            
            if tds > SOLIDS_MAX:
                print(Fore.RED + f"TDS ALTO: {tds} (Limite: {SOLIDS_MAX}). Acqua molto mineralizzata.")
                reset_color()
                self.declare(Fact(problema_solidi="alto"))
                self.problems_found += 1
            elif tds > avg_tds:
                print(Fore.YELLOW + f"Attenzione: TDS ({tds}) superiore alla media del dataset ({avg_tds:.0f}).")
                reset_color()
        except ValueError: pass

        # DUREZZA
        print("Inserisci la Durezza (Hardness) in mg/L:")
        try:
            hard = float(input())
            if hard > HARDNESS_LIMIT:
                 print(Fore.YELLOW + "Acqua molto Dura.")
                 reset_color()
                 self.declare(Fact(acqua_dura="si"))
        except ValueError: pass

        self.declare(Fact(fine_analisi="si"))

    # --- REGOLE LABORATORI AGGIORNATE ---

    @Rule(OR(Fact(problema_ph="acido"), Fact(problema_ph="basico")))
    def book_chemical_lab(self):
        print(Fore.CYAN + "[CSP] Richiesta turno LABORATORIO CHIMICO..." + Fore.RESET)
        # Passiamo "chemical" per trovare il Dr. Rossi o i chimici
        self._run_scheduler("chemical")

    @Rule(OR(Fact(problema_torbidita="alta"), Fact(problema_solidi="alto")))
    def book_physical_lab(self):
        print(Fore.CYAN + "[CSP] Richiesta turno MANUTENZIONE FISICA..." + Fore.RESET)
        # Passiamo "physical" per trovare idraulici o tecnici
        self._run_scheduler("physical")
        
    @Rule(AND(Fact(problema_ph=MATCH.p), Fact(problema_torbidita="alta")))
    def critical_contamination(self):
        print(Fore.RED + "\n!!! CONTAMINAZIONE CRITICA RILEVATA !!!" + Fore.RESET)
        print(Fore.MAGENTA + "[CSP] ⚠️ ATTIVAZIONE SQUADRA EMERGENZA..." + Fore.RESET)
        # Passiamo "critical" per la squadra speciale
        self._run_scheduler("critical")

    # --- CONCLUSIONI ---

    @Rule(Fact(fine_analisi="si"))
    def final_report(self):
        print(Fore.CYAN + "\n=== REPORT FINALE ===")
        if self.problems_found == 0:
            print(Fore.GREEN + "L'acqua risulta POTABILE e conforme agli standard analizzati.")
        else:
            print(Fore.RED + f"L'acqua NON è sicura. Rilevate {self.problems_found} anomalie.")
        reset_color()

    def _run_scheduler(self, issue_type):
        """Esegue il CSP cercando turni specifici per il tipo di problema"""
        try:
            # Chiama il tuo scheduler.py aggiornato
            csp = laboratory_csp(issue_type=issue_type)
            solutions = csp.get_solutions_list()
            
            if solutions:
                print(f"   >> Turno Assegnato: {solutions[0]}")
            else:
                print(Fore.RED + "   >> NESSUN TURNO DISPONIBILE (Verificare vincoli!)" + Fore.RESET)
        except Exception as e:
            print(f"   >> Errore Scheduler: {e}")
