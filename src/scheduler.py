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
        
        # Vincolo Rossi: Non lavora mai di Lunedì
        self.addConstraint(lambda staff, giorno: not (staff == "Dr. Rossi (Chimico Senior)" and giorno == "Lunedi"), ["staff", "giorno"])

        # Vincolo Verdi: Solo turni mattina (supervisionato)
        self.addConstraint(lambda staff, turno: not (staff == "Dr. Verdi (Chimico Junior)" and "Pomeriggio" in turno), ["staff", "turno"])

        # --- VINCOLI SPECIFICI PER LABORATORIO (Logica recuperata dal tuo snippet) ---

        if self.issue_type == 'chemical':
            # Il Laboratorio Chimico è aperto solo:
            # - Lunedì (Mattina)
            # - Giovedì (Pomeriggio)
            def orari_chimica(giorno, turno):
                if giorno == "Lunedi" and "Mattina" in turno: return True
                if giorno == "Giovedi" and "Pomeriggio" in turno: return True
                return False # Chiuso negli altri orari
            
            self.addConstraint(orari_chimica, ["giorno", "turno"])

        elif self.issue_type == 'physical':
            # Il Laboratorio Fisico è aperto solo:
            # - Martedì (Mattina)
            # - Venerdì (Pomeriggio)
            def orari_fisica(giorno, turno):
                if giorno == "Martedi" and "Mattina" in turno: return True
                if giorno == "Venerdi" and "Pomeriggio" in turno: return True
                return False
            
            self.addConstraint(orari_fisica, ["giorno", "turno"])

    def get_solutions_list(self):
        """Restituisce le soluzioni formattate e ordinate"""
        solutions = self.getSolutions()
        formatted_solutions = []
        
        priority = {"Lunedi": 1, "Martedi": 2, "Mercoledi": 3, "Giovedi": 4, "Venerdi": 5}
        # Ordina per giorno e poi per turno
        solutions.sort(key=lambda x: (priority.get(x["giorno"], 99), x["turno"]))

        for s in solutions:
            sol_str = f"📅 {s['giorno']} - 🕒 {s['turno']} | 👤 {s['staff']}"
            formatted_solutions.append(sol_str)
            
        return formatted_solutions