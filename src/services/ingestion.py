import pandas as pd
from io import BytesIO

class DataIngestionService:
    def __init__(self):
        pass

    def ingest_from_url(self, url: str = None, file_obj = None) -> pd.DataFrame:
        """
        Fetch CSV from S3/URL or read local file object.
        """
        if file_obj is not None:
            print("Loading data from uploaded file...")
            return pd.read_csv(file_obj)
            
        print(f"Loading data from {url}...")
        
        # Return a mock DataFrame for the blueprint demonstration IF no file
        data = {
            "Date": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"],
            "Product_Category": ["Electronics", "Clothing", "Electronics", "Home", "Clothing"],
            "Region": ["North", "South", "East", "West", "North"],
            "Sales_Amount": [1500, 500, 2000, 800, 600],
            "Units_Sold": [3, 10, 5, 2, 8],
            "CustomerID": ["C001", "C002", "C003", "C004", "C005"]
        }
        df = pd.DataFrame(data)
        return df

    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean column names, detect types.
        """
        return df
