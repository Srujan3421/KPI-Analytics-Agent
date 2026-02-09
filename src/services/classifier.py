import pandas as pd
from src.llm.client import LLMClient
from src.llm.prompts import Prompts
from src.models.domain import DomainClassification
import json

class DomainClassifier:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def classify(self, df: pd.DataFrame) -> DomainClassification:
        """
        Sample data and ask LLM for domain.
        """
        prompt = Prompts.DOMAIN_CLASSIFICATION.format(
            columns=list(df.columns),
            sample=df.head(3).to_markdown()
        )
        response_str = self.llm.generate(prompt, json_mode=True)
        data = json.loads(response_str)
        
        # Unwrapping logic for inconsistent LLM JSON structure
        if isinstance(data, dict):
             # 1. Check for specific wrapper keys
             for key in ['output', 'response', 'classification', 'result']:
                 if key in data and isinstance(data[key], dict):
                     data = data[key]
                     break
             else:
                 # 2. Heuristic: if keys (e.g. 'domain') are missing but there is only 1 key which is a dict, take it
                 required_keys = {'domain', 'dataset_type', 'summary', 'confidence'}
                 if not required_keys.intersection(data.keys()):
                     # If we don't have the required keys at top level
                     if len(data) == 1:
                         first_val = next(iter(data.values()))
                         if isinstance(first_val, dict):
                             data = first_val

        return DomainClassification(**data)
