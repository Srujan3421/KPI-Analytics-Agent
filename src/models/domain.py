from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

class KPI(BaseModel):
    id: str = Field(..., description="Unique identifier for the KPI")
    name: str = Field(..., description="Display name of the KPI")
    description: str = Field(..., description="Explanation of what the KPI measures")
    unit: Optional[str] = Field(None, description="Unit of measurement (e.g., USD, %)")
    calculation_logic: str = Field(..., description="Logic/formula description")
    visualization_type: Optional[str] = Field("bar", description="Recommended chart type: bar, line, pie, donut, scatter, metric")

class Card(BaseModel):
    title: str = Field(..., description="Title of the KPI card")
    kpi_id: str = Field(..., description="Reference to the KPI definition")
    relevance_score: float = Field(..., description="Relevance score (0-1)")
    visual_type: str = Field("line", description="Preferred visualization type")

class DataPoint(BaseModel):
    kpi_id: str
    data: List[Dict[str, Any]] = Field(..., description="List of rows/points for the chart")
    extracted_at: datetime = Field(default_factory=datetime.now)
    title: Optional[str] = None
    chart_type: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None

class DescriptiveAnalysis(BaseModel):
    kpi_id: str
    summary_text: str = Field(..., description="Short textual entry describing the trend")
    insights: List[str] = Field(default_factory=list, description="Key bullet points")

class DomainClassification(BaseModel):
    domain: str = Field(..., description="E.g., Finance, Retail")
    dataset_type: str = Field(..., description="Transactional, Time-series, etc.")
    summary: str
    confidence: float
