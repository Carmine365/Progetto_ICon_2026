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
        Recupera le descrizioni dei parametri salvate nelle proprietà dell'ontologia.
        Utile per spiegare all'utente cosa significa 'Torbidità' o 'pH'.
        """
        if not self.ontology:
            return

        dict_params_onto = {}

        # Itera su tutti gli individui (es. pH, Hardness, Solids...)
        for i in self.ontology.individuals():
            # NOTA: Nell'ontologia devi aver creato la proprietà "descrizione_parametro"
            # Se l'individuo ha una descrizione, la salviamo
            if hasattr(i, "descrizione_parametro"):
                # Gestione sicura per evitare errori se la lista è vuota
                desc = i.descrizione_parametro
                dict_params_onto[str(i)] = desc if desc else ["Descrizione non disponibile"]
            else:
                # Fallback se manca la proprietà
                dict_params_onto[str(i)] = ["Descrizione non disponibile"]

        for k in dict_params_onto.keys():
            k1 = k
            # PULIZIA NOME: Rimuove il prefisso dell'ontologia per avere solo il nome pulito
            # Es: "water_quality.istanza_pH" diventa "pH"
            k1 = k1.replace("water_quality.istanza_", "")
            k1 = k1.replace("water_quality.", "") # Sicurezza extra
            
            self.dict_parameters[k1] = dict_params_onto[k]

    def print_parameters(self):
        """
        Stampa a video la lista dei parametri disponibili e le loro descrizioni.
        """
        i = 1
        dict_nums_params = {}
        dict_nums_keys = {}

        if not self.dict_parameters:
            print("Nessun parametro caricato dall'ontologia.")
            return {}, {}

        for k in self.dict_parameters.keys():
            # Prende la prima stringa della descrizione (owlready restituisce liste)
            desc_text = self.dict_parameters[k][0] if isinstance(self.dict_parameters[k], list) else self.dict_parameters[k]
            
            print(f"Parametro [{i}]: {k}")
            print(f"   Descrizione: {desc_text}")
            print("-" * 30)
            
            dict_nums_params[i] = self.dict_parameters[k]
            dict_nums_keys[i] = k
            i = i + 1

        return dict_nums_params, dict_nums_keys