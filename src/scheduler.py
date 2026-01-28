from constraint import *

class laboratoryCsp(Problem):
    """
    Gestisce la pianificazione dei turni di manutenzione usando 
    la teoria dei Constraint Satisfaction Problems (CSP).
    """

    def __init__(self, issue_type="general"):
        super().__init__()
        self.issue_type = issue_type
        
        # --- 1. DEFINIZIONE VARIABILI E DOMINI (Teoria Cap. 3) ---
        
        # Variabile: STAFF (Il dominio cambia in base al tipo di problema rilevato dall'Esperto)
        if self.issue_type == 'chemical':
            # Se il problema è pH o Solfati, servono Chimici
            staff_domain = ["Dr. Rossi (Chimico Senior)", "Dr. Verdi (Chimico Junior)"]
        elif self.issue_type == 'physical':
            # Se il problema è Torbidità o Tubi, servono Tecnici
            staff_domain = ["Ing. Bianchi (Manutenzione)", "Tecnico Neri (Idraulico)"]
        elif self.issue_type == 'critical':
            # Se c'è rischio corrosione, serve il team d'assalto
            staff_domain = ["SQUADRA EMERGENZA", "Responsabile Sicurezza"]
        else:
            staff_domain = ["Tecnico Generico"]

        self.addVariable("staff", staff_domain)
        
        # Variabile: GIORNO
        self.addVariable("giorno", ["Lunedi", "Martedi", "Mercoledi", "Giovedi", "Venerdi"])
        
        # Variabile: TURNO
        self.addVariable("turno", ["Mattina (08-14)", "Pomeriggio (14-20)"])

        # --- 2. APPLICAZIONE VINCOLI (Constraints) ---
        self.apply_constraints()

    def apply_constraints(self):
        """
        Definisce le regole che limitano le soluzioni validi.
        """
        
        # VINCOLO 1: Disponibilità del Dr. Rossi (Non lavora mai di Lunedì)
        def vincolo_rossi_no_lunedi(staff, giorno):
            if staff == "Dr. Rossi (Chimico Senior)" and giorno == "Lunedi":
                return False # Soluzione scartata
            return True
        
        self.addConstraint(vincolo_rossi_no_lunedi, ["staff", "giorno"])

        # VINCOLO 2: Il Junior non può lavorare da solo nei turni critici (es. Pomeriggio tardi)
        # (Qui semplificato: Verdi lavora solo di Mattina per supervisione)
        def vincolo_verdi_solo_mattina(staff, turno):
            if staff == "Dr. Verdi (Chimico Junior)" and "Pomeriggio" in turno:
                return False
            return True
            
        self.addConstraint(vincolo_verdi_solo_mattina, ["staff", "turno"])

        # VINCOLO 3: La Squadra Emergenza è disponibile sempre (nessun vincolo restrittivo)

    def get_solutions_list(self):
        """
        Restituisce le soluzioni formattate per l'utente.
        """
        solutions = self.getSolutions()
        formatted_solutions = []
        
        # Ordiniamo per giorno per leggibilità
        priority = {"Lunedi": 1, "Martedi": 2, "Mercoledi": 3, "Giovedi": 4, "Venerdi": 5}
        solutions.sort(key=lambda x: priority.get(x["giorno"], 99))

        for s in solutions:
            sol_str = f"{s['giorno']} - {s['turno']}: {s['staff']}"
            formatted_solutions.append(sol_str)
            
        return formatted_solutions