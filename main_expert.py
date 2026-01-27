# --- FUNZIONI MAIN ---

from src.expert_system import WaterExpert
from src.ontology_manager import water_ontology


def main_agent():
    expert_agent = WaterExpert()
    expert_agent.reset()
    
    try:
        # Questo avvia il motore. Visto che le regole ora contengono gli input(),
        # l'interazione partirà automaticamente da qui.
        expert_agent.run()
    except KeyboardInterrupt:
        print("\n\n[!] Interruzione utente rilevata. Torno al menu...")
    except Exception as e:
        print(f"\n[!] Errore imprevisto durante l'analisi: {e}")

    # expert_agent.print_facts() # Decommentare per debug

def main_ontology():
    try:
        do = water_ontology()
        do.get_parameters_descriptions()
        params, keys_params = do.print_parameters()

        if not params:
            print("Nessun parametro trovato nell'ontologia.")
            return

        print("\nSeleziona il parametro di cui vuoi conoscere la descrizione (inserisci numero):")
        
        while True:
            try:
                scelta = input("Numero (o 'q' per uscire): ")
                if scelta.lower() == 'q': break
                
                param_number = int(scelta)
                if param_number not in params.keys():
                    print("Numero non valido. Riprova:")
                    continue
                
                # Gestione sicura nel caso la descrizione sia una lista o stringa
                desc = params[param_number]
                desc_str = ' '.join(desc) if isinstance(desc, list) else str(desc)
                
                print(f"\n📘 PARAMETRO: {keys_params[param_number]}")
                print(f"ℹ️  DESCRIZIONE: {desc_str}")
                break
            except ValueError:
                print("Inserisci un numero valido.")
    except Exception as e:
        print(f"Errore modulo ontologia: {e}")

if __name__ == '__main__':
    exit_program = False

    print("Benvenuto in WATER QUALITY EXPERT, sistema esperto per l'analisi della potabilità.")
    while not exit_program:
        print("\n-----------> MENU <-----------\n[1] Enciclopedia Parametri (Ontologia)\n[2] Analisi Nuovo Campione (Sistema Esperto)\n[3] Esci")
        
        try:
            user_choose = int(input("Scelta: "))
        except ValueError:
            user_choose = 0

        if user_choose == 1:
            main_ontology()
        elif user_choose == 2:
            main_agent()
        elif user_choose == 3:
            print("Chiusura programma...")
            exit_program = True
        else:
            print("Scelta non valida.")