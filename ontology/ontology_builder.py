import os
from owlready2 import *

# Percorso salvataggio
base_path = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(base_path, "water_quality.owl")

# 1. Creazione Ontologia
onto = get_ontology("http://test.org/water_quality.owl")

with onto:
    
    # --- A. CLASSI BASE ---
    class WaterSample(Thing):
        pass

    class Parameter(Thing):
        pass

    # --- B. DATA PROPERTIES (Tutti i parametri) ---
    class has_ph_value(DataProperty):
        domain = [WaterSample]; range = [float]

    class has_hardness_value(DataProperty):
        domain = [WaterSample]; range = [float]

    class has_solids_value(DataProperty):
        domain = [WaterSample]; range = [float]

    class has_chloramines_value(DataProperty):
        domain = [WaterSample]; range = [float]

    class has_sulfate_value(DataProperty):
        domain = [WaterSample]; range = [float]

    class has_conductivity_value(DataProperty):
        domain = [WaterSample]; range = [float]

    class has_organic_carbon_value(DataProperty):
        domain = [WaterSample]; range = [float]

    class has_trihalomethanes_value(DataProperty):
        domain = [WaterSample]; range = [float]

    class has_turbidity_value(DataProperty):
        domain = [WaterSample]; range = [float]
        
    class descrizione_parametro(DataProperty):
        domain = [Parameter]; range = [str]

    # --- C. CLASSI DI RISCHIO (Definizioni Formali per il Reasoner) ---
    
    # 1. pH (Acido < 6.5, Basico > 8.5)
    class AcidicWater(WaterSample):
        equivalent_to = [WaterSample & has_ph_value.some(ConstrainedDatatype(float, max_exclusive=6.5))]

    class BasicWater(WaterSample):
        equivalent_to = [WaterSample & has_ph_value.some(ConstrainedDatatype(float, min_exclusive=8.5))]

    # 2. Solfati (> 250)
    class HighSulfateWater(WaterSample):
        equivalent_to = [WaterSample & has_sulfate_value.some(ConstrainedDatatype(float, min_exclusive=250.0))]

    # 3. Torbidità (> 5.0)
    class TurbidWater(WaterSample):
        equivalent_to = [WaterSample & has_turbidity_value.some(ConstrainedDatatype(float, min_exclusive=5.0))]

    # 4. Solidi Totali (> 1000)
    class HighSolidsWater(WaterSample):
        equivalent_to = [WaterSample & has_solids_value.some(ConstrainedDatatype(float, min_exclusive=1000.0))]

    # 5. Cloramine (> 4.0)
    class HighChloraminesWater(WaterSample):
        equivalent_to = [WaterSample & has_chloramines_value.some(ConstrainedDatatype(float, min_exclusive=4.0))]

    # 6. Conducibilità (> 800)
    class HighConductivityWater(WaterSample):
        equivalent_to = [WaterSample & has_conductivity_value.some(ConstrainedDatatype(float, min_exclusive=800.0))]

    # 7. Carbonio Organico (> 10.0)
    class HighCarbonWater(WaterSample):
        equivalent_to = [WaterSample & has_organic_carbon_value.some(ConstrainedDatatype(float, min_exclusive=10.0))]

    # 8. Trialometani (> 80.0)
    class HighTHMWater(WaterSample):
        equivalent_to = [WaterSample & has_trihalomethanes_value.some(ConstrainedDatatype(float, min_exclusive=80.0))]
        
    # 9. Durezza (> 300)
    class HardWater(WaterSample):
        equivalent_to = [WaterSample & has_hardness_value.some(ConstrainedDatatype(float, min_exclusive=300.0))]

    # Classe Riassuntiva: Acqua Non Sicura
    class UnsafeWater(WaterSample):
        equivalent_to = [
            AcidicWater | BasicWater | HighSulfateWater | TurbidWater | 
            HighSolidsWater | HighChloraminesWater | HighCarbonWater | HighTHMWater
        ]

    # --- D. CASO COMPLESSO (CorrosiveWater) ---
    # Definito come intersezione: pH < 6.0 AND Sulfate > 200.0
    class CorrosiveWater(WaterSample):
        equivalent_to = [
            WaterSample & 
            has_ph_value.some(ConstrainedDatatype(float, max_exclusive=6.0)) &
            has_sulfate_value.some(ConstrainedDatatype(float, min_exclusive=200.0))
        ]

    # --- E. INDIVIDUI (Per le descrizioni nella GUI) ---
    
    ph = Parameter("ph")
    ph.descrizione_parametro = ["Indica quanto l'acqua è acida o basica. Range sicuro WHO: 6.5 - 8.5."]
    
    hardness = Parameter("Hardness")
    hardness.descrizione_parametro = ["Causata da sali di calcio e magnesio."]

    solids = Parameter("Solids") 
    solids.descrizione_parametro = ["Totale solidi disciolti (minerali, sali). Limite: 1000 mg/l."]

    chloramines = Parameter("Chloramines")
    chloramines.descrizione_parametro = ["Disinfettanti usati nei sistemi idrici. Limite: 4 mg/l."]

    sulfate = Parameter("Sulfate")
    sulfate.descrizione_parametro = ["Sostanza naturale. Alte concentrazioni alterano il gusto. Limite: 250 mg/l."]

    conductivity = Parameter("Conductivity")
    conductivity.descrizione_parametro = ["Conducibilità elettrica. Limite: 800 uS/cm."]

    organic_carbon = Parameter("Organic_carbon")
    organic_carbon.descrizione_parametro = ["Quantità totale di carbonio organico. Limite: 10 ppm."]

    trihalomethanes = Parameter("Trihalomethanes")
    trihalomethanes.descrizione_parametro = ["Sottoprodotti della clorazione. Cancerogeni sopra 80 ug/l."]

    turbidity = Parameter("Turbidity")
    turbidity.descrizione_parametro = ["Nuvolosità dell'acqua. WHO raccomanda < 5.0 NTU."]
    
    potability_status = Parameter("PotabilityStatus")
    potability_status.descrizione_parametro = ["Indica se l'acqua è sicura (1) o no (0)."]

# 2. SALVATAGGIO
try:
    if os.path.exists(output_path):
        os.remove(output_path) # Rimuove la vecchia versione per sicurezza
    onto.save(file=output_path)
    print(f"✅ Ontologia salvata con successo in: {output_path}")
    print("   -> Generati 9 parametri + 11 Classi di Rischio (inclusa CorrosiveWater)")
except Exception as e:
    print(f"❌ Errore durante il salvataggio: {e}")