import pandas as pd
import numpy as np
import pandas.api.types as ptypes

class DataCleaningService:
    def __init__(self):
        self.report = []

    def log(self, message):
        self.report.append(message)
        print(f"[Cleaner] {message}")

    def clean_dataset(self, df: pd.DataFrame, numeric_imputation: str = 'median', categorical_imputation: str = 'mode') -> pd.DataFrame:
        """
        Execute the 6-step robust cleaning pipeline.
        Args:
            df: Input DataFrame
            numeric_imputation: 'median', 'mean', or 'zero'
            categorical_imputation: 'mode' or 'drop'
        """
        self.report = []
        df = df.copy()
        
        # Step 1: Handling Missing Values
        df = self._handle_missing_values(df, numeric_imputation, categorical_imputation)
        
        # Step 2: Remove Duplicates
        df = self._remove_duplicates(df)
        
        # Step 3: Fix Data Types (Dates & Numbers)
        df = self._fix_data_types(df)
        
        # Step 4: Outlier Detection (Capping)
        df = self._handle_outliers(df)
        
        # Step 5: Feature Engineering
        df = self._feature_engineering(df)
        
        return df

    def _handle_missing_values(self, df: pd.DataFrame, numeric_strat: str, cat_strat: str) -> pd.DataFrame:
        self.log(f"Handling Missing Values (Numeric: {numeric_strat}, Categorical: {cat_strat})...")
        
        # Numeric Imputation
        nums = df.select_dtypes(include=['number']).columns
        for col in nums:
            missing = df[col].isnull().sum()
            if missing > 0:
                if numeric_strat == 'median':
                    val = df[col].median()
                    df[col] = df[col].fillna(val)
                    self.log(f"Filled {missing} missing in {col} with median: {val}")
                elif numeric_strat == 'mean':
                    val = df[col].mean()
                    df[col] = df[col].fillna(val)
                    self.log(f"Filled {missing} missing in {col} with mean: {val}")
                elif numeric_strat == 'zero':
                    df[col] = df[col].fillna(0)
                    self.log(f"Filled {missing} missing in {col} with 0")
                elif numeric_strat == 'drop':
                     df = df.dropna(subset=[col])
                     self.log(f"Dropped rows with missing {col}")

        # Categorical Imputation
        cats = df.select_dtypes(include=['object', 'category']).columns
        for col in cats:
            missing = df[col].isnull().sum()
            if missing > 0:
                if cat_strat == 'mode':
                    if not df[col].mode().empty:
                        val = df[col].mode()[0]
                        df[col] = df[col].fillna(val)
                        self.log(f"Filled {missing} missing in {col} with mode: {val}")
                elif cat_strat == 'drop':
                     df = df.dropna(subset=[col])
                     self.log(f"Dropped rows with missing {col}")
                # Else leave as is or fill 'Unknown'
                
        return df

    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        before = len(df)
        df = df.drop_duplicates()
        after = len(df)
        if before > after:
            self.log(f"Removed {before - after} duplicate rows.")
        return df

    def _fix_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        self.log("Fixing Data Types...")
        
        # 1. Clean likely numeric columns (currency, percent)
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check sample
                sample = df[col].dropna().iloc[0] if not df[col].dropna().empty else ""
                if isinstance(sample, str) and any(c.isdigit() for c in sample) and any(s in sample for s in ['$', ',', '%']):
                    try:
                        df[col] = df[col].astype(str).str.replace(r'[$,%]', '', regex=True)
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        self.log(f"Converted {col} to numeric.")
                    except:
                        pass
        
        # 2. Convert Dates
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    self.log(f"Converted {col} to datetime.")
                except:
                    pass
        return df

    def _handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        # Capping sensitive outliers using IQR
        nums = df.select_dtypes(include=['number']).columns
        for col in nums:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            if not outliers.empty:
                # Cap values instead of dropping
                df[col] = np.where(df[col] < lower_bound, lower_bound, df[col])
                df[col] = np.where(df[col] > upper_bound, upper_bound, df[col])
                self.log(f"Capped {len(outliers)} outliers in {col}.")
        return df

    def _feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        # Auto-detect Price/Quantity to creates Sales
        cols_lower = [c.lower() for c in df.columns]
        
        # Total Sales = Price * Quantity
        if 'total' not in ','.join(cols_lower):
            # Try to find price and quantity cols
            price_col = next((c for c in df.columns if 'price' in c.lower() or 'cost' in c.lower()), None)
            qty_col = next((c for c in df.columns if 'qty' in c.lower() or 'quantity' in c.lower() or 'units' in c.lower()), None)
            
            if price_col and qty_col and ptypes.is_numeric_dtype(df[price_col]) and ptypes.is_numeric_dtype(df[qty_col]):
                df['Total_Sales_Calc'] = df[price_col] * df[qty_col]
                self.log(f"Created 'Total_Sales_Calc' from {price_col} * {qty_col}")

        # Date extract
        date_col = next((c for c in df.columns if ptypes.is_datetime64_any_dtype(df[c])), None)
        if date_col:
            df['Month'] = df[date_col].dt.month_name()
            df['Year'] = df[date_col].dt.year
            df['DayOfWeek'] = df[date_col].dt.day_name()
            self.log(f"Extracted Month, Year, Day from {date_col}")
            
        return df

if __name__ == "__main__":
    # Test execution
    print("Initializing DataCleaningService...")
    cleaner = DataCleaningService()

    # Create dirty data for demonstration
    data = {
        "Date": ["2023-01-01", "2023-01-02", "2023-01-01", "2023-01-03", np.nan],
        "Product": ["Widget A", "Widget B", "Widget A", "Widget C", "Widget A"],
        "Price": ["$100", "200", "$100", "300.50", "5000"],
        "Qty": [10, 5, 10, 2, 1],
        "Category": ["X", "Y", "X", np.nan, "X"]
    }
    
    print("\\n--- Original DataFrame ---")
    df = pd.DataFrame(data)
    print(df)
    
    print("\\n--- Cleaning Data ---")
    cleaned_df = cleaner.clean_dataset(df)
    
    print("\\n--- Report ---")
    for line in cleaner.report:
        print(f"- {line}")
        
    print("\\n--- Cleaned DataFrame ---")
    print(cleaned_df)
