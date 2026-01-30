from constraint import *

class laboratoryCsp(Problem):
    """
    Gestisce la pianificazione dei turni usando CSP.
    Integra vincoli specifici per tipo di laboratorio.
    """

    def __init__(self, issue_type="general"):
        super().__init__()
        self.issue_type = issue_type
        
        # 1. VARIABILI
        
        # Staff: dipende dal problema
        if self.issue_type == 'chemical':
            staff_domain = ["Dr. Rossi (Chimico Senior)", "Dr. Verdi (Chimico Junior)"]
        elif self.issue_type == 'physical':
            staff_domain = ["Ing. Bianchi (Manutenzione)", "Tecnico Neri (Idraulico)"]
        elif self.issue_type == 'critical':
            staff_domain = ["SQUADRA EMERGENZA", "Responsabile Sicurezza"]
        else:
            staff_domain = ["Tecnico Generico"]

        self.addVariable("staff", staff_domain)
        self.addVariable("giorno", ["Lunedi", "Martedi", "Mercoledi", "Giovedi", "Venerdi"])
        self.addVariable("turno", ["Mattina (08-14)", "Pomeriggio (14-20)"])

        # 2. VINCOLI
        self.apply_constraints()

    def apply_constraints(self):
        
        # --- VINCOLI GENERALI ---
        
        # 1. Dr. Rossi (Senior):
        # CORREZIONE: Invece di "Mai Lunedì", diciamo che non lavora Venerdì Pomeriggio (Weekend lungo).
        # Questo lascia 9 slot disponibili su 10.
        self.addConstraint(
            lambda staff, giorno, turno: not (staff == "Dr. Rossi (Chimico Senior)" and giorno == "Venerdi" and "Pomeriggio" in turno), 
            ["staff", "giorno", "turno"]
        )

        # 2. Dr. Verdi (Junior):
        # CORREZIONE: Invece di "Solo Mattina", diciamo che evita i turni critici del Lunedì Mattina (riunione).
        self.addConstraint(
            lambda staff, giorno, turno: not (staff == "Dr. Verdi (Chimico Junior)" and giorno == "Lunedi" and "Mattina" in turno), 
            ["staff", "giorno", "turno"]
        )

        # --- VINCOLI SPECIFICI PER LABORATORIO (Logica recuperata dal tuo snippet) ---

        if self.issue_type == 'chemical':
            # Il Laboratorio Chimico è aperto:
            # - Lunedì, Mercoledì, Giovedì (Tutto il giorno)
            # - Venerdì (Solo Mattina per pulizia filtri)
            # - Martedì (CHIUSO per approvvigionamento)
            def orari_chimica(giorno, turno):
                days_full = ["Lunedi", "Mercoledi", "Giovedi"]
                if giorno in days_full: return True
                if giorno == "Venerdi" and "Mattina" in turno: return True
                return False
            
            self.addConstraint(orari_chimica, ["giorno", "turno"])

        elif self.issue_type == 'physical':
            # Il Laboratorio Fisico è aperto:
            # - Martedì, Venerdì (Tutto il giorno)
            # - Giovedì (Solo Pomeriggio)
            # - Lunedì, Mercoledì (CHIUSO)
            def orari_fisica(giorno, turno):
                if giorno in ["Martedi", "Venerdi"]: return True
                if giorno == "Giovedi" and "Pomeriggio" in turno: return True
                return False
            
            self.addConstraint(orari_fisica, ["giorno", "turno"])

    def get_solutions_list(self):
        """Restituisce le soluzioni formattate e ordinate per priorità temporale."""
        solutions = self.getSolutions()
        formatted_solutions = []
        
        if not solutions:
            return [f"⚠️ NESSUN TURNO DISPONIBILE per '{self.issue_type}'. (Vincoli troppo stretti)"]

        # Dizionario per ordinare i giorni della settimana
        priority = {"Lunedi": 1, "Martedi": 2, "Mercoledi": 3, "Giovedi": 4, "Venerdi": 5}
        
        # Ordina per giorno (1-5) e poi per turno (alfabetico: Mattina prima di Pomeriggio se 'M' < 'P'.. no, ma raggruppa bene)
        solutions.sort(key=lambda x: (priority.get(x["giorno"], 99), x["turno"]))

        for s in solutions:
            # Icone diverse per mattina/pomeriggio per leggibilità
            icon_turno = "☀️" if "Mattina" in s['turno'] else "🌒"
            sol_str = f"📅 {s['giorno']} | {icon_turno} {s['turno']} | 👤 {s['staff']}"
            formatted_solutions.append(sol_str)
            
        return formatted_solutions