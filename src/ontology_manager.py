from owlready2 import *
import os

class water_ontology:
    def __init__(self):
        # CARICAMENTO: Assicurati che il file .owl si chiami così
        # Nota: get_ontology vuole il percorso completo o relativo
        path = os.path.join("ontology", "water_quality.owl")
        self.ontology = get_ontology(path).load()
        self.dict_parameters = {}

    def get_parameters_descriptions(self):
        dict_params_onto = {}

        # Itera su tutti gli individui (es. pH, Hardness, Solids...)
        for i in self.ontology.individuals():
            # NOTA: Nell'ontologia devi aver creato la proprietà "descrizione_parametro"
            # Se l'individuo ha una descrizione, la salviamo
            if hasattr(i, "descrizione_parametro"):
                dict_params_onto[str(i)] = i.descrizione_parametro
            else:
                # Fallback se manca la descrizione
                dict_params_onto[str(i)] = ["Descrizione non disponibile"]

        for k in dict_params_onto.keys():
            k1 = k
            # PULIZIA NOME: Rimuove il prefisso dell'ontologia per avere solo il nome pulito
            # Es: "water_quality.istanza_pH" diventa "pH"
            k1 = k1.replace("water_quality.istanza_", "")
            k1 = k1.replace("water_quality.", "") # Sicurezza extra
            
            self.dict_parameters[k1] = dict_params_onto[k]

    def print_parameters(self):
        i = 1
        dict_nums_params = {}
        dict_nums_keys = {}

        for k in self.dict_parameters.keys():
            print("Parametro [%d]: Nome: %s" % (i, k))
            
            dict_nums_params[i] = self.dict_parameters[k]
            dict_nums_keys[i] = k
            i = i + 1

        return dict_nums_params, dict_nums_keys