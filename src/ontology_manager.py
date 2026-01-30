from owlready2 import get_ontology, sync_reasoner_pellet, destroy_entity, DataPropertyClass
import os

# 1. Rinominiamo la classe in 'water_ontology' (snake_case) 
# per farla coincidere con la chiamata in main_expert.py
class waterOntology: 
    def __init__(self):
        # Definizione Percorso Ontologia
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(BASE_DIR, "ontology", "water_quality.owl")

        self.ontology = None
        self.dict_parameters = {}

        # Caricamento Ontologia
        print(f"--- Caricamento Ontologia: {path} ---")
        try:
            self.ontology = get_ontology(path).load()
            self._sanitize_strings_for_reasoner()
        except Exception as e:
            print(f"[ERRORE] Impossibile caricare l'ontologia: {e}")
            return

        # Carichiamo i parametri disponibili
        self.load_parameters()

    def _sanitize_strings_for_reasoner(self):
        """
        Rimuove caratteri illegali (come l'apostrofo) dalle proprietà stringa.
        """
        if not self.ontology: return
        try:
            for i in self.ontology.individuals():
                for prop in i.get_properties():
                    if isinstance(prop, DataPropertyClass):
                        values = getattr(i, prop.name)
                        new_values = []
                        changed = False
                        for v in values:
                            if isinstance(v, str) and "'" in v:
                                new_values.append(v.replace("'", " "))
                                changed = True
                            else:
                                new_values.append(v)
                        if changed:
                            setattr(i, prop.name, new_values)
        except Exception as e:
            print(f"Errore sanitizzazione: {e}")

    def load_parameters(self):
        """Scansiona l'ontologia per trovare parametri e descrizioni."""
        if not self.ontology: return

        self.dict_parameters = {} 
        for i in self.ontology.individuals():
            clean_name = i.name 
            
            # Recupero descrizione
            desc_text = "Descrizione non disponibile."
            if hasattr(i, "descrizione_parametro") and i.descrizione_parametro:
                desc_raw = i.descrizione_parametro
                desc_text = desc_raw[0] if isinstance(desc_raw, list) else str(desc_raw)

            self.dict_parameters[clean_name] = desc_text

    # --- METODI MANCANTI AGGIUNTI PER IL MAIN ---
    
    def get_parameters_descriptions(self):
        """Metodo richiesto dal main_expert.py."""
        self.load_parameters()

    def print_parameters(self):
        """
        Stampa i parametri e RESTITUISCE i dizionari per il menu del main.
        """
        print("\n--- PARAMETRI NELL'ONTOLOGIA ---")
        
        indexed_descriptions = {}
        indexed_names = {}
        
        if not self.dict_parameters:
            print("Nessun parametro caricato.")
            return {}, {}

        # Creiamo un indice numerico per il menu (1, 2, 3...)
        for idx, (name, desc) in enumerate(self.dict_parameters.items(), 1):
            print(f"[{idx}] {name}")
            indexed_descriptions[idx] = desc
            indexed_names[idx] = name
            
        # Restituisce esattamente i due valori che main_expert.py si aspetta
        return indexed_descriptions, indexed_names

    # ------------------------------------------------------------

    def get_parameter_description(self, param_name):
        return self.dict_parameters.get(param_name, "Nessuna descrizione trovata.")

    def semantic_check(self, ph, sulfate):
        """Verifica semantica dinamica per l'integrazione con la GUI."""
        if not self.ontology: return False
        
        is_corrosive = False
        try:
            with self.ontology:
                temp_sample = self.ontology.WaterSample("Temp_User_Sample")
                temp_sample.has_ph_value = [float(ph)]
                temp_sample.has_sulfate_value = [float(sulfate)]

                sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)
                
                corrosive_class = getattr(self.ontology, "CorrosiveWater", None)
                if corrosive_class and corrosive_class in temp_sample.is_a:
                    is_corrosive = True

                destroy_entity(temp_sample)
        except Exception as e:
            print(f"[ERRORE REASONER] {e}")
            
        return is_corrosive

    def get_threshold(self, class_name, property_name, default_value):
        """
        Cerca nella definizione della classe OWL una restrizione numerica.
        Supporta 'is_a', 'equivalent_to' e intersezioni logiche (&).
        """
        if not self.ontology:
            return default_value

        try:
            # 1. Trova la classe
            owl_class = self.ontology.search_one(iri=f"*{class_name}")
            if not owl_class:
                return default_value

            # 2. Crea una lista di definizioni da ispezionare (is_a + equivalent_to)
            definitions = list(owl_class.is_a) + list(owl_class.equivalent_to)

            for restriction in definitions:
                # Caso A: La restrizione è diretta (es. has_ph_value some ...)
                # Caso B: La restrizione è in un'intersezione (es. WaterSample & has_ph_value some ...)
                
                # Se è un'intersezione (AND), owlready2 ha l'attributo 'Classes'
                targets = [restriction]
                if hasattr(restriction, "Classes"):
                    targets = restriction.Classes

                # Controlliamo ogni componente
                for target in targets:
                    if hasattr(target, "property") and hasattr(target, "value"):
                        
                        if target.property.name == property_name:
                            val = target.value
                            
                            # Estrazione valore (float semplice)
                            if isinstance(val, (int, float)):
                                return float(val)
                                
                            # Estrazione valore (ConstrainedDatatype es. < 6.5)
                            if hasattr(val, "max_exclusive"): return float(val.max_exclusive)
                            if hasattr(val, "min_exclusive"): return float(val.min_exclusive)
                            if hasattr(val, "max_inclusive"): return float(val.max_inclusive)
                            if hasattr(val, "min_inclusive"): return float(val.min_inclusive)

        except Exception as e:
            print(f"[WARN] Impossibile estrarre soglia per {class_name}: {e}")
        
        # Se non troviamo nulla, torniamo il default
        return default_value

# Istanza globale
manager = waterOntology()