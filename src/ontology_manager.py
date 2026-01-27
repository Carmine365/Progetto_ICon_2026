from owlready2 import *
import os

class water_ontology:
    def __init__(self):
        # 1. Definizione Percorso Ontologia
        path = os.path.join("ontology", "water_quality.owl")
        self.ontology = None
        self.dict_parameters = {}

        # 2. Caricamento e Ragionamento (MODIFICA CHIAVE)
        try:
            print(f"--- Caricamento Ontologia: {path} ---")
            self.ontology = get_ontology(path).load()
            
            # -----------------------------------------------------

            # --- BLOCCO INFERENZA (Migliorato per il Punto 1) ---
            print("Avvio del Reasoner (Pellet) per l'inferenza semantica...")
            try:
                with self.ontology:
                    # 1. Creiamo un campione di prova "invisibile" per testare il reasoner
                    test_sample = self.ontology.WaterSample("Campione_Test_Inferenza")
                    test_sample.has_ph_value = [5.0]  # Valore acido!

                    # 2. Sincronizziamo il reasoner
                    sync_reasoner_pellet() 

                    # 3. Verifichiamo se il reasoner lo ha riclassificato
                    # is_a contiene le classi a cui appartiene l'individuo
                    print(f"   > Classi inferite per pH=5.0: {test_sample.is_a}")
                    
                    # Controllo specifico per la demo
                    # Nota: owlready2 a volte mette le classi nell'ordine inverso o usa riferimenti
                    classes_names = [c.name for c in test_sample.is_a if hasattr(c, 'name')]
                    if "AcidicWater" in classes_names:
                        print(f"   ✅ SUCCESSO: Il reasoner ha dedotto autonomamente che è 'AcidicWater'!")
                    else:
                        print(f"   ⚠️ ATTENZIONE: Inferenza non scattata. Classi attuali: {classes_names}")

                    # Pulizia: distruggiamo il campione test per non sporcare l'ontologia in memoria
                    destroy_entity(test_sample)

            except Exception as e_reasoner:
                print(f"⚠️ Warning Reasoner: {e_reasoner}")
                # ... (gestione errore esistente) ...

            # -----------------------------------------------------
            # --- BLOCCO INFERENZA (Teoria Cap. 6) ---
            # Attiviamo il Reasoner (Pellet) per dedurre nuova conoscenza.
            # Questo trasforma l'ontologia da semplice "schema" a "motore semantico".
            print("Avvio del Reasoner (Pellet) per l'inferenza semantica...")
            try:
                with self.ontology:
                    sync_reasoner_pellet() 
                print("✅ Inferenza completata: relazioni implicite derivate.")
            except Exception as e_reasoner:
                print(f"⚠️ Warning: Il Reasoner non è partito (Manca Java o Pellet?).")
                print(f"Dettaglio errore: {e_reasoner}")
                print("Il sistema continuerà in modalità 'Sola Lettura' (senza inferenza).")
            # ----------------------------------------

        except Exception as e:
            print(f"❌ Errore critico nel caricamento ontologia: {e}")

    def get_parameters_descriptions(self):
        """
        Recupera le descrizioni pulite usando direttamente l'attributo .name
        """
        if not self.ontology:
            return

        # Svuotiamo il dizionario per sicurezza
        self.dict_parameters = {}

        # Itera su tutti gli individui (es. pH, Hardness...)
        for i in self.ontology.individuals():
            # 1. Recupero Nome Pulito (La modifica chiave)
            # Invece di str(i) che dà "ontology.ph", i.name dà solo "ph" o "Hardness"
            clean_name = i.name 
            
            # 2. Recupero Descrizione
            if hasattr(i, "descrizione_parametro") and i.descrizione_parametro:
                # owlready2 restituisce spesso una lista per le proprietà testo
                desc_raw = i.descrizione_parametro
                desc_text = desc_raw[0] if isinstance(desc_raw, list) else str(desc_raw)
            else:
                desc_text = "Descrizione non disponibile nell'ontologia."

            # 3. Salvataggio nel dizionario
            self.dict_parameters[clean_name] = desc_text

    def print_parameters(self):
        """
        Stampa solo l'elenco dei nomi per il menu di scelta.
        """
        i = 1
        dict_nums_params = {}
        dict_nums_keys = {}

        if not self.dict_parameters:
            print("Nessun parametro caricato dall'ontologia.")
            return {}, {}

        print("\n--- PARAMETRI DISPONIBILI ---")
        for k in self.dict_parameters.keys():
            # MODIFICA: Stampiamo solo [Numero] Nome
            # La descrizione la mostriamo solo quando l'utente sceglie!
            print(f"[{i}] {k}")
            
            dict_nums_params[i] = self.dict_parameters[k]
            dict_nums_keys[i] = k
            i = i + 1

        return dict_nums_params, dict_nums_keys