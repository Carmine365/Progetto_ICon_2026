from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

class WaterRiskBayesianNetwork:
    def __init__(self):
        # Definiamo la struttura della rete (Causa -> Effetto)
        # VicinanzaIndustrie -> InquinamentoChimico
        # PioggiaIntensa -> Torbidita
        self.model = DiscreteBayesianNetwork([
            ('VicinanzaIndustrie', 'InquinamentoChimico'),
            ('PioggiaIntensa', 'TorbiditaAumentata'),
            ('InquinamentoChimico', 'RischioTotale'),
            ('TorbiditaAumentata', 'RischioTotale')
        ])

        # 1. CPD per VicinanzaIndustrie (0=No, 1=Sì)
        # Supponiamo che nel 20% dei casi ci siano industrie vicine
        cpd_ind = TabularCPD(variable='VicinanzaIndustrie', variable_card=2, values=[[0.8], [0.2]])

        # 2. CPD per PioggiaIntensa (0=No, 1=Sì)
        cpd_rain = TabularCPD(variable='PioggiaIntensa', variable_card=2, values=[[0.7], [0.3]])

        # 3. CPD per InquinamentoChimico (condizionato da Industrie)
        # Se NO industrie: Prob inquinamento bassa (5%)
        # Se SI industrie: Prob inquinamento alta (60%)
        cpd_chem = TabularCPD(variable='InquinamentoChimico', variable_card=2, 
                              values=[[0.95, 0.40], 
                                      [0.05, 0.60]],
                              evidence=['VicinanzaIndustrie'], evidence_card=[2])

        # 4. CPD per TorbiditaAumentata (condizionato da Pioggia)
        cpd_turb = TabularCPD(variable='TorbiditaAumentata', variable_card=2,
                              values=[[0.90, 0.20], 
                                      [0.10, 0.80]],
                              evidence=['PioggiaIntensa'], evidence_card=[2])

        # 5. CPD per RischioTotale (condizionato da Chimico e Torbidità)
        # Combinazioni: (F,F), (F,T), (T,F), (T,T)
        cpd_risk = TabularCPD(variable='RischioTotale', variable_card=2,
                              values=[[0.99, 0.60, 0.40, 0.05],  # Probabilità NO Rischio
                                      [0.01, 0.40, 0.60, 0.95]], # Probabilità SI Rischio
                              evidence=['InquinamentoChimico', 'TorbiditaAumentata'],
                              evidence_card=[2, 2])

        # Aggiungiamo le probabilità al modello
        self.model.add_cpds(cpd_ind, cpd_rain, cpd_chem, cpd_turb, cpd_risk)
        
        # Validiamo il modello
        assert self.model.check_model()
        
        # Inizializziamo il motore di inferenza
        self.infer = VariableElimination(self.model)

    def get_risk_probability(self, industrie_presenti, pioggia_intensa):
        """
        Calcola la probabilità di rischio (0-1) date le evidenze.
        """
        # Mappiamo i booleani a interi (0, 1)
        evidence = {
            'VicinanzaIndustrie': 1 if industrie_presenti else 0,
            'PioggiaIntensa': 1 if pioggia_intensa else 0
        }
        
        try:
            # Eseguiamo l'inferenza
            result = self.infer.query(variables=['RischioTotale'], evidence=evidence)
            
            # Restituiamo la probabilità che RischioTotale sia 1 (Sì)
            return result.values[1]
        except Exception as e:
            print(f"[BAYES ERROR] {e}")
            return 0.5 # Valore neutro di fallback