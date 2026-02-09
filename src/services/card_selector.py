from typing import List
import json
from src.llm.client import LLMClient
from src.llm.prompts import Prompts
from src.models.domain import Card, KPI

class CardSelector:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def select_top_cards(self, kpis: List[KPI]) -> List[Card]:
        """
        Select top 3 KPIs for the dashboard.
        """
        kpi_summary = [{"id": k.id, "name": k.name, "desc": k.description} for k in kpis]
        prompt = Prompts.CARD_SELECTION.format(kpis=str(kpi_summary))
        response_str = self.llm.generate(prompt, json_mode=True)
        data = json.loads(response_str)
        
        # Handle dict wrapping
        if isinstance(data, dict):
            for val in data.values():
                if isinstance(val, list):
                    cards_data = val
                    break
            else:
                cards_data = []
        elif isinstance(data, list):
            cards_data = data
        else:
            cards_data = []

        return [Card(**c) for c in cards_data]
