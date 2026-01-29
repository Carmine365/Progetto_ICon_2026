import numpy as np
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

class WaterRiskBayesianNetwork:
    """
    Rete Bayesiana per la stima del rischio idrico basata su conoscenza esperta.
    
    NOTA: Poiché il dataset CSV non contiene dati storici su 'VicinanzaIndustrie' 
    o 'PioggiaIntensa', le probabilità condizionate (CPD) sono stimate 
    a priori basandosi su regole di dominio (Expert Knowledge) e non apprese dai dati.
    """

    def __init__(self, prob_industrie=0.2, prob_pioggia=0.3):
        """
        Inizializza la rete con probabilità configurabili.
        
        Args:
            prob_industrie (float): Probabilità a priori che ci siano industrie vicine (0-1).
            prob_pioggia (float): Probabilità a priori di piogge intense (0-1).
        """
        self.model = DiscreteBayesianNetwork([
            ('VicinanzaIndustrie', 'InquinamentoChimico'),
            ('OdoreSospetto', 'InquinamentoChimico'),
            ('SaporeMetallico', 'InquinamentoChimico'),  # <--- NUOVO
            
            ('PioggiaIntensa', 'TorbiditaAumentata'),
            ('OsservazioneTorbidita', 'TorbiditaAumentata'), # <--- NUOVO
            
            ('InquinamentoChimico', 'RischioTotale'),
            ('TorbiditaAumentata', 'RischioTotale')
        ])
        
        self._setup_cpds(prob_industrie, prob_pioggia)
        
        # Validazione modello
        if not self.model.check_model():
            raise ValueError("Errore nella definizione della Rete Bayesiana: le CPD non sono coerenti.")
            
        self.infer = VariableElimination(self.model)

    def _setup_cpds(self, p_ind, p_rain):
        """Definisce le Tabelle di Probabilità Condizionata (CPT)."""
        
        # 1. Nodi Radice (Priori)
        cpd_ind = TabularCPD(variable='VicinanzaIndustrie', variable_card=2, 
                             values=[[1 - p_ind], [p_ind]]) # 0=No, 1=Sì

        cpd_rain = TabularCPD(variable='PioggiaIntensa', variable_card=2, 
                              values=[[1 - p_rain], [p_rain]]) # 0=No, 1=Sì

        # 2. CPD OdoreSospetto (0=No, 1=Sì) - NUOVO
        # Supponiamo che nel 10% dei casi l'acqua abbia un odore strano a priori
        cpd_odor = TabularCPD(variable='OdoreSospetto', variable_card=2, values=[[0.9], [0.1]])

        # 3. Sapore (5% prob - evento raro ma grave)
        cpd_taste = TabularCPD(variable='SaporeMetallico', variable_card=2, values=[[0.95], [0.05]])

        # 5. Vista Torbida (10% prob)
        cpd_visual = TabularCPD(variable='OsservazioneTorbidita', variable_card=2, values=[[0.9], [0.1]])

        # --- NODI INTERMEDI ---

        # 6. Inquinamento Chimico
        # Dipende da: Industrie (I), Odore (O), Sapore (S)
        # Combinazioni totali: 2*2*2 = 8 colonne
        # Ordine evidence: Industrie, Odore, Sapore
        # (F,F,F), (F,F,T), (F,T,F), (F,T,T), (T,F,F), (T,F,T), (T,T,F), (T,T,T)
        cpd_chem = TabularCPD(
            variable='InquinamentoChimico', variable_card=2,
            evidence=['VicinanzaIndustrie', 'OdoreSospetto', 'SaporeMetallico'], 
            evidence_card=[2, 2, 2],
            values=[
                # Prob NO Inquinamento
                [0.95, 0.40, 0.40, 0.05, 0.60, 0.10, 0.10, 0.01], 
                # Prob SI Inquinamento (Complementare)
                [0.05, 0.60, 0.60, 0.95, 0.40, 0.90, 0.90, 0.99]
            ]
        )
        # Nota come il Sapore (T) o l'Odore (O) da soli alzano il rischio al 60% anche senza industrie!

        # 7. Torbidità Aumentata
        # Dipende da: Pioggia (P), Osservazione (V)
        # Ordine evidence: Pioggia, Osservazione
        # (F,F), (F,T), (T,F), (T,T)
        cpd_turb = TabularCPD(
            variable='TorbiditaAumentata', variable_card=2,
            evidence=['PioggiaIntensa', 'OsservazioneTorbidita'], 
            evidence_card=[2, 2],
            values=[
                # Prob NO Torbidità
                [0.95, 0.10, 0.20, 0.05], 
                # Prob SI Torbidità
                [0.05, 0.90, 0.80, 0.95]
            ]
        )
        # Se vedo torbido (colonna 2), la probabilità schizza al 90% indipendentemente dalla pioggia.

        # --- NODO FINALE ---
        
        # 8. Rischio Totale (uguale a prima)
        cpd_risk = TabularCPD(variable='RischioTotale', variable_card=2,
                              values=[[0.99, 0.60, 0.40, 0.05],
                                      [0.01, 0.40, 0.60, 0.95]],
                              evidence=['InquinamentoChimico', 'TorbiditaAumentata'],
                              evidence_card=[2, 2])

        # Aggiunta CPD al modello
        self.model.add_cpds(cpd_ind, cpd_odor, cpd_taste, cpd_rain, cpd_visual, cpd_chem, cpd_turb, cpd_risk)
        assert self.model.check_model()
        self.infer = VariableElimination(self.model)

    def get_risk_probability(self, has_industry: bool, heavy_rain: bool, odore_presente, taste, visual) -> float:
        """
        Calcola la probabilità condizionata di Rischio Totale date le evidenze osservate.
        """
        evidence = {
            'VicinanzaIndustrie': 1 if has_industry else 0,
            'PioggiaIntensa': 1 if heavy_rain else 0,
            'OdoreSospetto': 1 if odore_presente else 0,
            'SaporeMetallico': 1 if taste else 0,
            'OsservazioneTorbidita': 1 if visual else 0
        }
        
        try:
            result = self.infer.query(variables=['RischioTotale'], evidence=evidence)
            # Restituiamo la probabilità dell'evento 1 (Rischio Presente)
            return float(result.values[1])
        except Exception as e:
            print(f"[BAYES ERROR] Inferenza fallita: {e}")
            return 0.5 # Fallback neutro