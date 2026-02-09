import sys
import os
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.cleaning import DataCleaningService

def test_cleaning():
    print("Initializing DataCleaningService...")
    cleaner = DataCleaningService()

    # Create dirty data
    data = {
        "Date": ["2023-01-01", "2023-01-02", "2023-01-01", "2023-01-03", np.nan], # Duplicate date, missing date
        "Product": ["Widget A", "Widget B", "Widget A", "Widget C", "Widget A"], # Duplicates
        "Price": ["$100", "200", "$100", "300.50", "5000"], # String currency, outlier
        "Qty": [10, 5, 10, 2, 1],
        "Category": ["X", "Y", "X", np.nan, "X"] # Missing category
    }
    
    df = pd.DataFrame(data)
    print("\n--- Original DataFrame ---")
    print(df)
    
    print("\n--- Running Cleaning Pipeline ---")
    cleaned_df = cleaner.clean_dataset(df)
    
    print("\n--- Cleaning Report ---")
    for line in cleaner.report:
        print(f"- {line}")
        
    print("\n--- Cleaned DataFrame ---")
    print(cleaned_df)
    print("\ndtypes:")
    print(cleaned_df.dtypes)

if __name__ == "__main__":
    test_cleaning()
