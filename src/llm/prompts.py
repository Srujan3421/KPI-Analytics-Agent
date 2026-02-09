class Prompts:

    DOMAIN_CLASSIFICATION = """
You are a data analyst.

Analyze the dataset and identify its business or data domain.

Columns: {columns}
Sample rows: {sample}

Rules:
- Do not guess a specific business if unsure.
- Use generic domain names if needed (e.g. "Operational Data", "Transaction Data", "Sensor Data").
- Base your answer only on the column meanings.

Return STRICT JSON only:
{{
  "domain": "...",
  "dataset_type": "...",
  "summary": "...",
  "confidence": 0.0
}}
"""


    KPI_GENERATION = """
You are a universal data analyst.

Dataset domain: {domain}
Columns: {columns}

Task:
Design 6–10 meaningful KPIs.

Rules:
1. First classify columns into:
   - Measures (numeric, continuous)
   - Dimensions (categorical, date/time)
   - Identifiers (ids, codes, keys)

2. NEVER use identifier columns in KPIs.

3. Each KPI must:
   - Combine ONE measure and ONE dimension (if possible)
   - Use aggregation: SUM, AVG, COUNT, MIN, MAX, or RATIO
   - Be useful for understanding performance, distribution, or trends
   - Avoid trivial metrics (e.g., "Total rows")

4. Prefer:
   - Measure by category
   - Measure over time
   - Top-N by measure
   - Distribution of measures

Each KPI must include:
- name
- description
- calculation_logic
- unit
- visualization_type (bar/line/pie/scatter/metric)
- dimension_hint (column name)

Return STRICT JSON only:
[
  {{
    "name": "...",
    "description": "...",
    "calculation_logic": "...",
    "unit": "...",
    "visualization_type": "bar/line/pie/scatter/metric",
    "dimension_hint": "column_name"
  }}
]
"""


    CHART_GENERATION = """
You are a universal BI chart generator.

Dataset columns: {columns}
Sample rows: {sample}

Task:
Generate ALL meaningful and important charts from this dataset.

Rules:
1. Classify columns into:
   - Measures (numeric)
   - Dimensions (categorical)
   - Time columns (date/datetime)
   - Identifiers (ids/keys)

2. NEVER use identifier columns for axes.

3. Charts must:
   - Have at least TWO categories or time points
   - Use one dimension (X) and one measure (Y)
   - Use aggregation (sum, mean, count, min, max)

4. Generate charts for:
   - EACH major categorical column vs EACH major numeric column
   - EACH time column vs EACH numeric column
   - Distribution of numeric columns
   - Top-N categories by numeric value
   - Correlation charts (numeric vs numeric when meaningful)

5. Cardinality handling:
   - ≤ 12 unique values → include all
   - > 12 unique values → Top 8 only

6. DO NOT generate:
   - Single-value charts
   - ID vs value charts
   - Duplicate charts
   - Charts with meaningless axes

7. Do NOT artificially limit the number of charts.
   Generate as many charts as are useful and non-redundant.

Each chart MUST include:
- title
- dimension
- measure
- aggregation
- chart_type (bar/line/pie/scatter/histogram/box)
- reason

Return STRICT JSON only:
[
  {{
    "title": "Measure by Dimension",
    "dimension": "column",
    "measure": "column",
    "aggregation": "sum",
    "chart_type": "bar",
    "reason": "Shows how the measure varies across categories"
  }}
]
"""


    INSIGHT_GENERATION = """
You are an analytical reporting system.

KPI name: {kpi_name}
Data points: {data_points}

Task:
Summarize patterns and insights.

Rules:
- Mention trends, highest/lowest values, or anomalies
- Do not repeat raw numbers
- Keep language business-friendly

Return STRICT JSON only:
{{
  "summary_text": "...",
  "insights": ["...", "..."]
}}
"""

    CHAT_WITH_DATA = """
You are a helpful data assistant.

Dataset Columns: {columns}
Sample Data (first 10 rows):
{sample_data}

User Question: {question}

Task:
Answer the user's question based on the provided sample data and column structure.
If the question requires aggregation that you cannot perform mentally on the sample, explain HOW you would calculate it (e.g., "I would sum column X grouped by column Y").
If the answer is visible in the sample, provide it directly.
Keep the answer concise and helpful.
"""
