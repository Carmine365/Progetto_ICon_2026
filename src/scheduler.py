from constraint import *

class laboratory_csp(Problem):

    def __init__(self, lab_name: str, solver=None):
        super().__init__(solver=solver)
        self.lab_name = lab_name
        # Giorni lavorativi
        self.days = self.addVariable("day", ["lunedi", "martedi", "mercoledi", "giovedi", "venerdi", "sabato"])
        # Orari possibili (0-23)
        self.hours = self.addVariable("hours", list(range(24)))
        self.availability = None

    def get_availability(self):
        # Risolve il problema (trova giorni/ore che soddisfano i vincoli aggiunti dall'esterno)
        self.availability = sorted(self.getSolutions(), key=lambda h: (h['day'], h['hours']))
        first_turn = None
        last_turn = None

        if len(self.availability) > 0:
            print(f"\n--- Turni disponibili per: {self.lab_name} ---")
            i = 0
            first_turn = i

            while i < len(self.availability):
                # Stampa formattata per sembrare un report tecnico
                print(f"ID [{i}] | Giorno: {self.availability[i]['day']:<10} | Orario: {self.availability[i]['hours']:02d}:00")
                i = i + 1
            
            last_turn = i - 1
            print("\n")
               
        else:
            print(f"Nessuna disponibilità trovata per {self.lab_name}.")

        return first_turn, last_turn
    
    def print_single_availability(self, index):
        if self.availability and index >= 0 and index < len(self.availability):
            print(f"Prenotazione Confermata: ID [{index}] - {self.availability[index]['day'].upper()} ore {self.availability[index]['hours']:02d}:00")
            print("Il tecnico è stato notificato.\n")