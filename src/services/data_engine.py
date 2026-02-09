import pandas as pd
import numpy as np
from src.models.domain import DataPoint

IMPORTANT_KEYWORDS_MEASURE = ["revenue", "amount", "price", "sales", "profit", "qty", "quantity", "count", "total"]
IMPORTANT_KEYWORDS_DIM = ["product", "item", "name", "category", "type", "size", "region", "store", "city"]


class DataPointEngine:
    def __init__(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("DataPointEngine requires a pandas DataFrame")

        self.df = df.copy()
        self.schema = self._analyze_schema()

    def _analyze_schema(self):
        schema = {"measures": [], "dimensions": [], "time": []}

        for col in self.df.columns:
            if np.issubdtype(self.df[col].dtype, np.number):
                schema["measures"].append(col)
            else:
                try:
                    pd.to_datetime(self.df[col])
                    schema["time"].append(col)
                except:
                    schema["dimensions"].append(col)

        schema["dimensions"] = [
            c for c in schema["dimensions"]
            if "id" not in c.lower() and self.df[c].nunique() > 1
        ]

        return schema

    # ---------------- PUBLIC API ----------------
    def generate_data_points(self, df: pd.DataFrame, kpis: list):
        charts = self.generate_important_charts()
        data_points = []

        for i, chart in enumerate(charts):
            kpi_id = kpis[i].id if i < len(kpis) else f"auto_{i}"

            dp = DataPoint(
                kpi_id=kpi_id,
                data=chart["data"],  # MUST be list
                title=chart["title"],
                chart_type=chart["chart_type"],
                x_label=chart["x_label"],
                y_label=chart["y_label"]
            )

            data_points.append(dp)

        return data_points

    # ---------------- CORE LOGIC ----------------
    def generate_important_charts(self):
        measures = self.schema["measures"]
        dims = self.schema["dimensions"]
        time_cols = self.schema["time"]

        measures = sorted(measures, key=self._score_measure, reverse=True)[:5]
        dims = sorted(dims, key=self._score_dimension, reverse=True)[:8]

        charts = []

        # 1. Time trends
        for t in time_cols[:1]:
            for m in measures:
                charts.append(self._time_vs_measure(t, m))
            charts.append(self._weekday_chart(t))

        # 2. Dimension vs measure
        for dim in dims:
            if self.df[dim].nunique() > 40:
                continue
            for m in measures:
                charts.append(self._dimension_vs_measure(dim, m))

        # 3. Distribution
        for m in measures:
            charts.append(self._distribution_chart(m))

        # 4. Correlation
        if len(measures) >= 2:
            for i in range(min(3, len(measures) - 1)):
                charts.append(self._correlation_chart(measures[i], measures[i + 1]))

        # filter useless
        final_charts = [c for c in charts if len(c["data"]) >= 2]

        return final_charts[:40]

    # ---------------- SCORING ----------------
    def _score_measure(self, col):
        return sum(2 for kw in IMPORTANT_KEYWORDS_MEASURE if kw in col.lower())

    def _score_dimension(self, col):
        return sum(2 for kw in IMPORTANT_KEYWORDS_DIM if kw in col.lower())

    # ---------------- CHART BUILDERS ----------------
    def _dimension_vs_measure(self, dim, measure):
        grp = (
            self.df.groupby(dim)[measure]
            .sum()
            .sort_values(ascending=False)
            .head(12)
            .reset_index()
        )

        return {
            "title": f"{measure.replace('_',' ').title()} by {dim.replace('_',' ').title()}",
            "chart_type": "bar",
            "x_label": dim.replace("_", " ").title(),
            "y_label": f"Total {measure.replace('_',' ').title()}",
            "data": [
                {"label": str(r[dim]), "value": float(r[measure])}
                for _, r in grp.iterrows()
                if pd.notna(r[measure])
            ]
        }

    def _time_vs_measure(self, time_col, measure):
        temp = self.df[[time_col, measure]].dropna()
        temp[time_col] = pd.to_datetime(temp[time_col])

        grp = temp.groupby(pd.Grouper(key=time_col, freq="M"))[measure].sum().reset_index()

        return {
            "title": f"Monthly {measure.replace('_',' ').title()}",
            "chart_type": "line",
            "x_label": "Month",
            "y_label": f"Total {measure.replace('_',' ').title()}",
            "data": [
                {"label": str(r[time_col].date()), "value": float(r[measure])}
                for _, r in grp.iterrows()
                if pd.notna(r[measure])
            ]
        }

    def _distribution_chart(self, measure):
        vals = self.df[measure].dropna()
        sample = vals.sample(min(300, len(vals)))

        return {
            "title": f"Distribution of {measure.replace('_',' ').title()}",
            "chart_type": "histogram",
            "x_label": measure.replace("_", " ").title(),
            "y_label": "Frequency",
            "data": [{"value": float(v)} for v in sample]
        }

    def _correlation_chart(self, m1, m2):
        temp = self.df[[m1, m2]].dropna()
        temp = temp.sample(min(300, len(temp)))

        return {
            "title": f"{m1.replace('_',' ').title()} vs {m2.replace('_',' ').title()}",
            "chart_type": "scatter",
            "x_label": m1.replace("_", " ").title(),
            "y_label": m2.replace("_", " ").title(),
            "data": [
                {"x": float(r[m1]), "y": float(r[m2])}
                for _, r in temp.iterrows()
            ]
        }

    def _weekday_chart(self, date_col):
        df = self.df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        df["weekday"] = df[date_col].dt.day_name()

        grp = df.groupby("weekday").size().reset_index(name="count")

        order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        grp["weekday"] = pd.Categorical(grp["weekday"], categories=order, ordered=True)
        grp = grp.sort_values("weekday")

        return {
            "title": "Records by Day of Week",
            "chart_type": "bar",
            "x_label": "Day of Week",
            "y_label": "Count",
            "data": [
                {"label": row["weekday"], "value": int(row["count"])}
                for _, row in grp.iterrows()
            ]
        }
