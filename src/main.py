import uuid
from src.services.ingestion import DataIngestionService
from src.services.classifier import DomainClassifier
from src.services.composer import KPIComposer
from src.services.card_selector import CardSelector
from src.services.data_engine import DataPointEngine
from src.services.analytics import DescriptiveAnalytics
from src.services.persistence import PersistenceLayer
from src.llm.client import LLMClient

from src.services.cleaning import DataCleaningService

class KPIAgent:
    def __init__(self):
        self.llm = LLMClient()
        self.ingestion = DataIngestionService()
        self.cleaner = DataCleaningService()
        self.classifier = DomainClassifier(self.llm)
        self.composer = KPIComposer(self.llm)
        self.card_selector = CardSelector(self.llm)
        self.data_engine = None
        self.analytics = DescriptiveAnalytics(self.llm)
        self.persistence = PersistenceLayer()

    def run(self, csv_url: str = None, file_obj = None, cleaning_params: dict = None):
        if cleaning_params is None:
            cleaning_params = {}
            
        session_id = str(uuid.uuid4())
        print(f"Starting Session: {session_id}")

        # 1. Ingestion
        df = self.ingestion.ingest_from_url(csv_url, file_obj)
        df = self.ingestion.normalize_columns(df)
        
        # 1.5 Cleaning (Robust)
        numeric_strat = cleaning_params.get("numeric_imputation", "median")
        cat_strat = cleaning_params.get("categorical_imputation", "mode")
        
        df = self.cleaner.clean_dataset(df, numeric_imputation=numeric_strat, categorical_imputation=cat_strat)
        
        # Capture Cleaning Report
        self.cleaning_report = self.cleaner.report

        # 2. Classification
        domain_info = self.classifier.classify(df)
        print(f"Detected Domain: {domain_info.domain}")

        # 3. KPI Generation
        kpis = self.composer.generate_kpis(domain_info.domain, list(df.columns))
        print(f"Generated {len(kpis)} KPIs")

        # 4. Card Selection
        selected_cards = self.card_selector.select_top_cards(kpis)

        # 5. Data Extraction & Analytics
        data_points = self.data_engine.generate_data_points(df, kpis)
        analyses = []
        # Optimization: Disabled per-graph AI analysis for speed
        # for kpi, dp in zip(kpis, data_points):
        #     analyses.append(self.analytics.analyze(kpi, dp))

        # 6. Persistence
        result = {
            "domain": domain_info.model_dump(mode='json'),
            "kpis": [k.model_dump(mode='json') for k in kpis],
            "cards": [c.model_dump(mode='json') for c in selected_cards],
            "data_points": [dp.model_dump(mode='json') for dp in data_points],
            "analyses": [a.model_dump(mode='json') for a in analyses],
            "cleaning_report": getattr(self, 'cleaning_report', [])
        }
        return session_id, result, df
