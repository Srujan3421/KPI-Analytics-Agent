from typing import List, Optional
import json
from src.llm.client import LLMClient
from src.llm.prompts import Prompts
from src.models.domain import DescriptiveAnalysis, DataPoint, KPI

class DescriptiveAnalytics:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def analyze(self, kpi: Optional[KPI], data_point: DataPoint) -> DescriptiveAnalysis:
        """
        Generate text insights based on the data trends.
        """
        # Fallback metadata if KPI is None (e.g. auto-generated charts)
        kpi_name = kpi.name if kpi else (data_point.title or "Unknown Metric")
        kpi_desc = kpi.description if kpi else f"Analysis of {kpi_name}"
        kpi_id = kpi.id if kpi else data_point.kpi_id

        # Convert data points to string representation for LLM
        # Limit data size to avoid context limit issues
        data_sample = data_point.data[:25] # Top 25 points
        data_str = json.dumps(data_sample)
        
        if len(data_point.data) > 25:
            data_str += f" ... (and {len(data_point.data)-25} more points)"

        prompt = Prompts.INSIGHT_GENERATION.format(
            kpi_name=kpi_name,
            kpi_desc=kpi_desc,
            data_points=data_str
        )
        
        try:
            response_str = self.llm.generate(prompt, json_mode=True)
            data = json.loads(response_str)
            
            return DescriptiveAnalysis(
                kpi_id=kpi_id,
                summary_text=data.get("summary_text", "No summary available."),
                insights=data.get("insights", [])
            )
        except Exception as e:
            print(f"Error generating insights for {kpi_name}: {e}")
            return DescriptiveAnalysis(
                kpi_id=kpi_id,
                summary_text="Analysis unavailable.",
                insights=["Could not generate insights due to an error."]
            )

    def chat_with_data(self, question: str, df: "pd.DataFrame") -> str:
        """
        Answer questions about the specific dataset using pandas AI or context-based checking.
        """
        # 1. Simple fallback: get basic stats to add to context
        # In a real agent, this would use pandas-ai or a SQL generator.
        # Here we did a simple approximation by feeding a sample.
        
        sample = df.head(10).to_string()
        cols = list(df.columns)
        
        prompt = Prompts.CHAT_WITH_DATA.format(
            question=question,
            columns=cols,
            sample_data=sample
        )
        
        try:
            return self.llm.generate(prompt)
        except Exception as e:
            return f"I couldn't analyze the data directly. Error: {e}"
