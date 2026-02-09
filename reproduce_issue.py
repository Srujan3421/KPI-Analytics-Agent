
import pandas as pd
import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))

try:
    from src.services.data_engine import DataPointEngine
    from src.models.domain import KPI
except ImportError:
    # If run from root, src should be importable if __init__.py exists or we treat it as package
    sys.path.append(os.getcwd())
    from src.services.data_engine import DataPointEngine
    from src.models.domain import KPI

def test_clean_data():
    print("Testing CLEAN data...")
    df = pd.DataFrame({
        "Product": ["A", "B", "C", "A", "B"],
        "Sales": [100, 200, 300, 150, 250],
        "Region": ["East", "West", "East", "West", "East"],
        "Date": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"]
    })
    
    engine = DataPointEngine(df)
    print(f"Schema: {engine.schema}")
    
    # Mock KPIs (though DataPointEngine usually auto-generates some without KPIs too?)
    # Wait, generate_data_points takes kpis list.
    # In generate_important_charts, it doesn't use KPIs, it uses schema.
    # generate_data_points calls generate_important_charts() then zips with KPIs.
    
    # Let's provide an empty list of KPIs to see if it generates auto-ids
    dps = engine.generate_data_points(df, [])
    
    print(f"Generated {len(dps)} data points.")
    for dp in dps:
        print(f" - {dp.title} ({dp.chart_type}) Data Len: {len(dp.data)}")

def test_dirty_data():
    print("\nTesting DIRTY data (strings as numbers)...")
    df = pd.DataFrame({
        "Product": ["A", "B", "C"],
        "Sales": ["$100", "$200", "$300"], # String!
        "Region": ["East", "West", "East"]
    })
    
    engine = DataPointEngine(df)
    print(f"Schema: {engine.schema}")
    
    dps = engine.generate_data_points(df, [])
    
    print(f"Generated {len(dps)} data points.")

if __name__ == "__main__":
    test_clean_data()
    test_dirty_data()
