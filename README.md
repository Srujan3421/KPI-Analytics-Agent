# KPI Agent Blueprint

This repository contains a blueprint for building an automated **KPI Agent**. This agent is designed to ingest raw data (CSV), classify its domain, generate relevant KPIs, and produce descriptive analytics using LLMs and PandasAI.

## 🚀 Objective

To build an intelligent system that automates the "Data Analyst" workflow:
1.  **Ingest & Clean**: Handle raw CSVs from S3.
2.  **Classify**: Determine the business domain (e.g., E-commerce, Finance).
3.  **Generate KPIs**: Create industry-standard metrics.
4.  **Visualize**: Select top cards and generate data points for charts.
5.  **Analyze**: Provide text-based insights for each KPI.
6.  **Persist**: Store everything in MongoDB for retrieval by the Frontend.

## 🛠 Tech Stack

-   **Language**: Python 3.10+
-   **LLM Orchestration**: [Groq](https://groq.com/) (Llama3-70b, Mistral, etc.).
-   **Data Processing**: Pandas, [PandasAI](https://github.com/gventuri/pandas-ai).
-   **Database**: MySQL.
-   **Frontend**: Streamlit.
-   **Testing**: Pytest.

## 📂 Repository Structure

```text
KPI-Agent-Blueprint/
├── README.md               # You are here
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── src/
│   ├── main.py             # Orchestrator Entry Point
│   ├── config.py           # Configuration loader
│   ├── models/             # Pydantic Data Models
│   │   └── domain.py       # KPI, Card, DataPoint definitions
│   ├── services/           # Core Business Logic
│   │   ├── ingestion.py    # Data Loading & Cleaning
│   │   ├── classifier.py   # Domain Classification (LLM)
│   │   ├── composer.py     # KPI Generation (LLM)
│   │   ├── card_selector.py# Top 3 Card Selection (LLM)
│   │   ├── data_engine.py  # Data extraction (PandasAI)
│   │   ├── analytics.py    # Descriptive Text (LLM)
│   │   └── persistence.py  # MongoDB Storage
│   ├── llm/                # LLM Integration
│   │   ├── client.py       # Wrapper for Groq
│   │   └── prompts.py      # System Prompts
│   └── ui/                 # Frontend
│       └── app.py          # Streamlit Dashboard
├── tests/                  # Unit & Integration Tests
└── scripts/
    └── run_sample.py       # Example run script
```

## ⚡ Quick Start

### 1. Prerequisites
-   Python 3.10+ installed.
-   MySQL instance running.
-   Groq API Key.

### 2. Setup

```bash
# Clone the repository
git clone <repository_url>
cd KPI-Agent-Blueprint

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure Environment
cp .env.example .env
# Edit .env and add your API Keys
```

### 3. Run the App

**Backend Pipeline (Test CLI):**
```bash
python scripts/run_sample.py
```

**Frontend Dashboard:**
```bash
streamlit run src/ui/app.py
```

## 🧪 Testing

```bash
pytest tests/
```

## 🏗 Architecture & Flow

1.  **Ingestion**: `DataIngestionService` loads CSV, cleans headers, parses dates.
2.  **Domain Classification**: `DomainClassifier` sends a data sample to Llama3 to detect the business context.
3.  **KPI Generation**: `KPIComposer` lists potential metrics based on columns and domain.
4.  **Card Selection**: `CardSelector` picks the top 3 most relevant KPIs.
5.  **Data Extraction**: `DataPointEngine` uses PandasAI to calculate the actual values/trends for the selected KPIs.
6.  **Analysis**: `DescriptiveAnalytics` looks at the trend data and writes a summary.
7.  **Persistence**: `PersistenceLayer` saves the entire JSON object to MySQL.
8.  **UI**: Streamlit reads from Mongo (or direct pipeline output) to display the Dashboard.
