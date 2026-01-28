from owlready2 import get_ontology, Thing, DataProperty, ConstrainedDatatype
# In app.py
from src.ontology_manager import manager as water_ontology 
# "manager" è l'istanza che hai appena creato in fondo al file

# 1. Crea l'ontologia
onto = get_ontology("http://test.org/water_quality.owl")

with onto:
    # --- 1. CLASSI BASE ---
    class WaterSample(Thing):
        """Un campione di acqua analizzato"""
        pass

    class Parameter(Thing):
        """Un parametro chimico-fisico dell'acqua"""
        pass

    # --- 2. DATA PROPERTIES (Le "colonne" del tuo dataset in OWL) ---
    class descrizione_parametro(DataProperty):
        """Descrizione testuale del parametro (per la documentazione)"""
        domain = [Parameter]
        range = [str]

    # 1. NUOVA PROPRIETÀ: Definiamo che un WaterSample può avere un valore di pH
    class has_ph_value(DataProperty):
        domain = [WaterSample]
        range = [float]

    # Proprietà per i Solfati
    class has_sulfate_value(DataProperty):
        domain = [WaterSample]
        range = [float]

    # Proprietà per la Torbidità
    class has_turbidity_value(DataProperty):
        domain = [WaterSample]
        range = [float]

    # --- REGOLA SWRL ---
        # "Se un campione ha pH < 6.0 E Solfati > 200.0, allora è CorrosiveWater"
        # Nota: swrlb:lessThan e swrlb:greaterThan sono built-in
        rule = Imp()
        rule.set_as_rule("""
            WaterSample(?w), 
            has_ph_value(?w, ?p), swrlb:lessThan(?p, 6.0), 
            has_sulfate_value(?w, ?s), swrlb:greaterThan(?s, 200.0) 
            -> CorrosiveWater(?w)
        """)

    # --- 3. CLASSI DEFINITE (Il "Motore Logico") ---
    # Classe A: Acqua Acida (pH < 6.5)
    class AcidicWater(WaterSample):
        equivalent_to = [WaterSample & has_ph_value.some(ConstrainedDatatype(float, max_exclusive=6.5))]

    # Classe B: Acqua con Solfati Alti (Sulfate > 250 - soglia WHO)
    class HighSulfateWater(WaterSample):
        equivalent_to = [WaterSample & has_sulfate_value.some(ConstrainedDatatype(float, min_exclusive=250.0))]

    # Classe C: Acqua Torbida (Turbidity > 5.0 - soglia WHO)
    class TurbidWater(WaterSample):
        equivalent_to = [WaterSample & has_turbidity_value.some(ConstrainedDatatype(float, min_exclusive=5.0))]

    # --- 4. LA CLASSE "UNSAFE" (Unione Logica) ---
    # Qui diciamo: "L'acqua NON sicura è quella che è Acida OPPURE ha Solfati Alti OPPURE è Torbida"
    # L'operatore "|" in owlready2 rappresenta l'OR logico (Union)
    class UnsafeWater(WaterSample):
        equivalent_to = [AcidicWater | HighSulfateWater | TurbidWater]

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