# --- FUNZIONI MAIN ---

from src.expert_system import WaterExpert
from src.ontology_manager import water_ontology


def main_agent():
    expert_agent = WaterExpert()
    expert_agent.reset()
    expert_agent.run()
    # expert_agent.print_facts() # Decommentare per debug

def main_ontology():
    # Usa la nuova classe WaterOntology
    do = water_ontology()
    do.get_parameters_descriptions()
    params, keys_params = do.print_parameters()

    print("\nSeleziona il parametro di cui vuoi conoscere la descrizione (inserisci numero):")
    try:
        param_number = int(input())
        while param_number not in params.keys():
            print("Numero non valido. Riprova:")
            param_number = int(input())
            
        print(f"\nPARAMETRO: {keys_params[param_number]}")
        print(f"DESCRIZIONE: {' '.join(params[param_number])}")
    except ValueError:
        print("Input non valido.")

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