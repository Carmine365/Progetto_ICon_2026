from owlready2 import get_ontology, sync_reasoner_pellet, destroy_entity
import os

class water_ontology:
    def __init__(self):
        # 1. Definizione Percorso Ontologia
        path = os.path.join("ontology", "water_quality.owl")
        self.ontology = None
        self.dict_parameters = {}

        # 2. Caricamento e Ragionamento (MODIFICA CHIAVE)
        print(f"--- Caricamento Ontologia: {path} ---")
        self.ontology = get_ontology(path).load()
        
        # --- BLOCCO INFERENZA (Teoria Cap. 6) ---
        # Attiviamo il Reasoner (Pellet) per dedurre nuova conoscenza.
        # Questo trasforma l'ontologia da semplice "schema" a "motore semantico".
        print("Avvio del Reasoner (Pellet) per l'inferenza semantica...")
        try:
            with self.ontology:
                # CASO 1: Creiamo un campione con Solfati pericolosi (300.0) e pH normale (7.0)
                unsafe_sample = self.ontology.WaterSample("Campione_Pericoloso_Solfati")
                unsafe_sample.has_sulfate_value = [300.0]
                unsafe_sample.has_ph_value = [7.0]

                # CASO 2: Creiamo un campione perfetto
                safe_sample = self.ontology.WaterSample("Campione_Sicuro")
                safe_sample.has_sulfate_value = [150.0]
                safe_sample.has_ph_value = [7.2]
                safe_sample.has_turbidity_value = [2.0]

                # Sincronizziamo il reasoner
                sync_reasoner_pellet() 

                # VERIFICA CASO 1
                print(f"\n🧪 Analisi Semantica 'Campione_Pericoloso_Solfati':")
                classes_1 = [c.name for c in unsafe_sample.is_a if hasattr(c, 'name')]
                print(f"   > Classi inferite: {classes_1}")
                
                if "UnsafeWater" in classes_1:
                    print("   ✅ SUCCESSO: Classificato come 'UnsafeWater' (tramite HighSulfateWater)!")
                
                # VERIFICA CASO 2
                print(f"\n💧 Analisi Semantica 'Campione_Sicuro':")
                classes_2 = [c.name for c in safe_sample.is_a if hasattr(c, 'name')]
                print(f"   > Classi inferite: {classes_2}")
                
                if "UnsafeWater" not in classes_2:
                    print("   ✅ SUCCESSO: NON è classificato come 'UnsafeWater'.")

                # Pulizia
                destroy_entity(unsafe_sample)
                destroy_entity(safe_sample)

        except Exception as e:
            print(f"Errore reasoner: {e}")

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