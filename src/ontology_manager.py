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

    def _extract_numeric_value(self, restriction_value):
        """Helper che estrae il float da qualsiasi tipo di restrizione (inclusive/exclusive)."""
        attrs = ["max_exclusive", "min_exclusive", "max_inclusive", "min_inclusive"]
        for attr in attrs:
            if hasattr(restriction_value, attr):
                return float(getattr(restriction_value, attr))
        return None

    def _recursive_search(self, entity, property_name):
        """Cerca ricorsivamente la restrizione sulla proprietà specificata."""
        # CASO BASE 1: È una restrizione sulla proprietà che cerchiamo
        if hasattr(entity, "property") and entity.property and entity.property.name == property_name:
            if hasattr(entity, "value"):
                return self._extract_numeric_value(entity.value)
        
        # CASO RICORSIVO: È una classe definita da intersezioni (es. "is_a" o "equivalent_to")
        # owlready2 usa .Classes per le intersezioni logiche (&)
        if hasattr(entity, "Classes"): 
            for sub_entity in entity.Classes:
                res = self._recursive_search(sub_entity, property_name)
                if res is not None: return res
                
        # Controlliamo anche le liste standard is_a / equivalent_to se passiamo una classe
        if hasattr(entity, "is_a"):
            for sub_entity in entity.is_a:
                res = self._recursive_search(sub_entity, property_name)
                if res is not None: return res

        if hasattr(entity, "equivalent_to"):
            for sub_entity in entity.equivalent_to:
                res = self._recursive_search(sub_entity, property_name)
                if res is not None: return res
                
        return None

    def get_threshold(self, class_name, property_name, default_value):
        """Metodo principale, cerca nella definizione della classe OWL una restrizione numerica."""
        if not self.ontology: return default_value
        
        try:
            owl_class = self.ontology.search_one(iri=f"*{class_name}")
            if not owl_class: return default_value

            # Avvio ricerca ricorsiva
            val = self._recursive_search(owl_class, property_name)
            
            if val is not None:
                return val
                
        except Exception as e:
            print(f"[WARN] Errore parsing soglia {class_name}: {e}")
            
        return default_value

# Istanza globale
manager = waterOntology()