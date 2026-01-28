from owlready2 import get_ontology, sync_reasoner_pellet, destroy_entity, Thing, Imp, DataPropertyClass
import os

class water_ontology:
    def __init__(self):
        # 1. Definizione Percorso Ontologia
        path = os.path.join("ontology", "water_quality.owl")
        self.ontology = None
        self.dict_parameters = {}

        # 2. Caricamento Ontologia
        print(f"--- Caricamento Ontologia: {path} ---")
        try:
            self.ontology = get_ontology(path).load()
        except Exception as e:
            print(f"[ERRORE] Impossibile caricare l'ontologia: {e}")
            return
        """
        # 3. BLOCCO INFERENZA DI TEST (Codice Originale Importante!)
        # Serve a dimostrare che il motore semantico funziona all'avvio
        print("Avvio del Reasoner (Pellet) per test di inferenza iniziale...")
        try:
            with self.ontology:

                # A. PULIZIA PREVENTIVA (Fix per il bug degli apostrofi)
                self._sanitize_strings_for_reasoner()

                # B. ESEMPIO DI "PIÙ INFERENZA": Aggiunta Regola SWRL Dinamica
                # Se non esiste già, aggiungiamo una regola che deduce "Danger" se pH < 5
                # (Questa è la vera potenza: creare regole logiche da codice)
                rule = Imp()
                rule.set_as_rule("WaterSample(?w), has_ph_value(?w, ?p), lessThan(?p, 5.0) -> CorrosiveWater(?w)")


                # Creiamo un campione di test sicuramente pericoloso
                test_sample = self.ontology.WaterSample("Test_Init_Sample")
                test_sample.has_sulfate_value = [300.0]  # Alto
                test_sample.has_ph_value = [7.0]         # Normale

                # Sincronizziamo il reasoner
                sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)

                # Verifichiamo se è stato classificato come Unsafe
                # (Assumendo che UnsafeWater o HighSulfateWater esistano nell'OWL)
                print(f"Test Classi Inferite: {test_sample.is_a}")
                
                # Pulizia dopo il test
                destroy_entity(test_sample)
                print("Test inferenza completato con successo.")
                
        except Exception as e:
            print(f"Warning: Reasoner non disponibile o errore nel test iniziale: {e}")
        """
        # 4. Carichiamo i parametri disponibili (Codice Originale)
        self.load_parameters()

    def _sanitize_strings_for_reasoner(self):
        """
        Rimuove caratteri illegali (come l'apostrofo) dalle proprietà stringa
        delle istanze per evitare il crash 'illegal escape sequence' di Pellet.
        """
        if not self.ontology:
            return
        try:
            for i in self.ontology.individuals():
                # Itera su tutte le proprietà dati dell'individuo
                for prop in i.get_properties():
                    # Se è una DataProperty e il valore è stringa
                    if isinstance(prop, DataPropertyClass):
                        values = getattr(i, prop.name)
                        new_values = []
                        changed = False
                        for v in values:
                            if isinstance(v, str) and "'" in v:
                                # Sostituisce l'apostrofo con uno spazio o nulla
                                v_clean = v.replace("'", " ") 
                                new_values.append(v_clean)
                                changed = True
                            else:
                                new_values.append(v)
                        
                        if changed:
                            setattr(i, prop.name, new_values)
                            # print(f"[FIX] Sanitizzata stringa in {i.name}.{prop.name}")
        except Exception as e:
            print(f"Errore durante sanitizzazione stringhe: {e}")

    def load_parameters(self):
        """
        Scansiona l'ontologia per trovare individui (parametri) e descrizioni.
        Rende il sistema dinamico: legge cosa c'è nell'OWL.
        """
        if not self.ontology: return

        for i in self.ontology.individuals():
            # Pulizia del nome (es. "ontology.ph" -> "ph")
            clean_name = i.name 
            
            # Recupero descrizione (se esiste la proprietà descrizione_parametro)
            desc_text = "Descrizione non disponibile."
            if hasattr(i, "descrizione_parametro") and i.descrizione_parametro:
                desc_raw = i.descrizione_parametro
                desc_text = desc_raw[0] if isinstance(desc_raw, list) else str(desc_raw)

            self.dict_parameters[clean_name] = desc_text

    def get_parameter_description(self, param_name):
        """Restituisce la descrizione semantica di un parametro."""
        return self.dict_parameters.get(param_name, "Nessuna descrizione trovata.")

    def print_parameters(self):
        """Utility per la CLI per mostrare i parametri."""
        print("\n--- PARAMETRI NELL'ONTOLOGIA ---")
        for k, v in self.dict_parameters.items():
            print(f"- {k}: {v}")

    # --- NUOVO METODO AGGIUNTO PER LA GUI ---
    def semantic_check(self, ph, sulfate):
        """
        Verifica semantica dinamica per l'integrazione con la GUI.
        """
        if not self.ontology: return False

        print(f"[ONTOLOGY] Check semantico dinamico: pH={ph}, Solfati={sulfate}")
        
        with self.ontology:
            # 1. Creiamo individuo temporaneo
            temp_sample = self.ontology.WaterSample("Temp_User_Sample")
            temp_sample.has_ph_value = [float(ph)]
            temp_sample.has_sulfate_value = [float(sulfate)]

            # 2. Reasoner
            try:
                sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)
            except Exception as e:
                print(f"[ERRORE REASONER] {e}")
                return False

            # 3. Check Classificazione SWRL (CorrosiveWater)
            is_corrosive = False
            corrosive_class = getattr(self.ontology, "CorrosiveWater", None)
            
            if corrosive_class and corrosive_class in temp_sample.is_a:
                is_corrosive = True

            # 4. Pulizia
            destroy_entity(temp_sample)
            
            return is_corrosive

# --- ISTANZA GLOBALE ---
manager = water_ontology()