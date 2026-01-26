from owlready2 import *

# 1. Crea l'ontologia
onto = get_ontology("http://test.org/water_quality.owl")

with onto:
    # 2. Definizione delle Classi
    class WaterSample(Thing):
        """Un campione di acqua analizzato"""
        pass

    class Parameter(Thing):
        """Un parametro chimico-fisico dell'acqua"""
        pass

    # 3. Definizione delle Proprietà
    class descrizione_parametro(DataProperty):
        """Descrizione testuale del parametro (per la documentazione)"""
        domain = [Parameter]
        range = [str]

    # 4. Creazione degli Individui (i parametri del CSV)
    # Creiamo le istanze esatte che il tuo codice water_ontology.py si aspetta

    ph = Parameter("ph")
    ph.descrizione_parametro = ["Indica quanto l'acqua è acida o basica. Range sicuro WHO: 6.5 - 8.5."]

    hardness = Parameter("Hardness")
    hardness.descrizione_parametro = ["Causata da sali di calcio e magnesio. Influenza la capacità di sciogliere sapone."]

    solids = Parameter("Solids") # Sarebbe il TDS
    solids.descrizione_parametro = ["Totale solidi disciolti (minerali, sali, metalli). Limite desiderabile: 500 mg/l."]

    chloramines = Parameter("Chloramines")
    chloramines.descrizione_parametro = ["Disinfettanti usati nei sistemi idrici pubblici. Livelli sicuri fino a 4 mg/L."]

    sulfate = Parameter("Sulfate")
    sulfate.descrizione_parametro = ["Sostanza naturale trovata in minerali. Alte concentrazioni possono alterare il gusto."]

    conductivity = Parameter("Conductivity")
    conductivity.descrizione_parametro = ["Misura la capacità dell'acqua di condurre corrente elettrica, legata ai minerali disciolti."]

    organic_carbon = Parameter("Organic_carbon")
    organic_carbon.descrizione_parametro = ["Misura della quantità totale di carbonio nei composti organici."]

    trihalomethanes = Parameter("Trihalomethanes")
    trihalomethanes.descrizione_parametro = ["Sottoprodotti chimici della clorazione. Livelli sicuri fino a 80 ppm."]

    turbidity = Parameter("Turbidity")
    turbidity.descrizione_parametro = ["Misura della nuvolosità dell'acqua dovuta a particelle sospese. WHO raccomanda < 5.00 NTU."]
    
    # Istanza speciale per il risultato finale
    potability_status = Parameter("PotabilityStatus")
    potability_status.descrizione_parametro = ["Indica se l'acqua è sicura per il consumo umano (1) o no (0)."]

# 5. Salvataggio del file .owl
output_file = "water_quality.owl"
onto.save(file=output_file)
print(f"Successo! Ontologia salvata come '{output_file}'. Ora puoi procedere con l'expert.")