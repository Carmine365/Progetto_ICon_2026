import os
from owlready2 import get_ontology, Thing, DataProperty, ConstrainedDatatype, Imp

# Definiamo il percorso assoluto per salvare il file nella cartella 'ontology'
base_path = os.path.dirname(os.path.abspath(__file__)) # Cartella dove si trova questo script
output_path = os.path.join(base_path, "water_quality.owl")

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

    # --- 2. DATA PROPERTIES ---
    class descrizione_parametro(DataProperty):
        domain = [Parameter]
        range = [str]

    class has_ph_value(DataProperty):
        domain = [WaterSample]
        range = [float]

    class has_sulfate_value(DataProperty):
        domain = [WaterSample]
        range = [float]

    class has_turbidity_value(DataProperty):
        domain = [WaterSample]
        range = [float]

    class CorrosiveWater(WaterSample):
        """Classe dedotta dalla regola SWRL"""
        pass

    # --- REGOLA SWRL ---
    # "Se pH < 6.0 E Solfati > 200.0 -> CorrosiveWater"
    # --- REGOLA SWRL ---
    # CORREZIONE: Rimuovere "swrlb:" e usare direttamente "lessThan" / "greaterThan"
    rule = Imp()
    rule.set_as_rule("""
        WaterSample(?w), 
        has_ph_value(?w, ?p), lessThan(?p, 6.0), 
        has_sulfate_value(?w, ?s), greaterThan(?s, 200.0) 
        -> CorrosiveWater(?w)
    """)

    # --- 3. CLASSI DEFINITE ---
    class AcidicWater(WaterSample):
        equivalent_to = [WaterSample & has_ph_value.some(ConstrainedDatatype(float, max_exclusive=6.5))]

    class HighSulfateWater(WaterSample):
        equivalent_to = [WaterSample & has_sulfate_value.some(ConstrainedDatatype(float, min_exclusive=250.0))]

    class TurbidWater(WaterSample):
        equivalent_to = [WaterSample & has_turbidity_value.some(ConstrainedDatatype(float, min_exclusive=5.0))]

    # --- 4. CLASSE UNSAFE ---
    class UnsafeWater(WaterSample):
        equivalent_to = [AcidicWater | HighSulfateWater | TurbidWater]

    

    # --- 5. CREAZIONE INDIVIDUI (Parametri) ---
    ph = Parameter("ph")
    ph.descrizione_parametro = ["Indica quanto l'acqua è acida o basica. Range sicuro WHO: 6.5 - 8.5."]

    hardness = Parameter("Hardness")
    hardness.descrizione_parametro = ["Causata da sali di calcio e magnesio."]

    solids = Parameter("Solids") 
    solids.descrizione_parametro = ["Totale solidi disciolti (minerali, sali). Limite: 1000 mg/l."]

    chloramines = Parameter("Chloramines")
    chloramines.descrizione_parametro = ["Disinfettanti usati nei sistemi idrici."]

    sulfate = Parameter("Sulfate")
    sulfate.descrizione_parametro = ["Sostanza naturale. Alte concentrazioni alterano il gusto."]

    conductivity = Parameter("Conductivity")
    conductivity.descrizione_parametro = ["Conducibilità elettrica legata ai minerali disciolti."]

    organic_carbon = Parameter("Organic_carbon")
    organic_carbon.descrizione_parametro = ["Quantità totale di carbonio organico."]

    trihalomethanes = Parameter("Trihalomethanes")
    trihalomethanes.descrizione_parametro = ["Sottoprodotti della clorazione."]

    turbidity = Parameter("Turbidity")
    turbidity.descrizione_parametro = ["Nuvolosità dell'acqua. WHO raccomanda < 5.0 NTU."]
    
    potability_status = Parameter("PotabilityStatus")
    potability_status.descrizione_parametro = ["Indica se l'acqua è sicura (1) o no (0)."]

# 6. SALVATAGGIO
try:
    if os.path.exists(output_path):
        os.remove(output_path) # Rimuove la vecchia versione per sicurezza
    onto.save(file=output_path)
    print(f"✅ Ontologia generata correttamente in: {output_path}")
except Exception as e:
    print(f"❌ Errore durante il salvataggio: {e}")