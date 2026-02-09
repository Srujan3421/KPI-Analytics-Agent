from typing import List
import json
import uuid
from src.llm.client import LLMClient
from src.llm.prompts import Prompts
from src.models.domain import KPI

class KPIComposer:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def generate_kpis(self, domain: str, columns: List[str]) -> List[KPI]:
        """
        Generate candidate KPIs based on domain and schema.
        """
        prompt = Prompts.KPI_GENERATION.format(domain=domain, columns=columns)
        response_str = self.llm.generate(prompt, json_mode=True)
        data = json.loads(response_str)
        
        # Handle case where LLM wraps list in a key like {"kpis": [...]}
        kpi_list = []
        if isinstance(data, list):
            kpi_list = data
        elif isinstance(data, dict):
            if "kpis" in data and isinstance(data["kpis"], list):
                kpi_list = data["kpis"]
            else:
                # Fallback: look for any list that looks like it contains KPIs
                for val in data.values():
                    if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict) and "name" in val[0]:
                        kpi_list = val
                        break
        
        # Filter out invalid entries
        valid_kpis = []
        for k in kpi_list:
            if isinstance(k, dict) and "name" in k and "calculation_logic" in k:
               valid_kpis.append(k)
        
        kpi_list = valid_kpis

        return [KPI(id=str(uuid.uuid4()), **k) for k in kpi_list]
