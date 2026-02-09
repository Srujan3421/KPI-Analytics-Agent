import streamlit as st
import pandas as pd
import plotly.express as px
import os, sys, uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.main import KPIAgent
from src.services.data_engine import DataPointEngine
from src.models.domain import KPI, DataPoint

st.set_page_config(page_title="KPI Agent", layout="wide")

# ---------------- STATE ----------------
if "agent" not in st.session_state:
    st.session_state.agent = KPIAgent()

if "page" not in st.session_state:
    st.session_state.page = "Upload"

if "data_state" not in st.session_state:
    st.session_state.data_state = {
        "df": None,
        "domain": None,
        "kpis": [],
        "data_points": [],
        "insights": []
    }

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("📊 KPI Agent")
    st.session_state.page = st.radio(
        "Navigation",
        ["Upload", "Preview", "Cleaning", "Dashboard", "Insights", "Chat with Data"]
    )

# ---------------- UPLOAD ----------------
if st.session_state.page == "Upload":
    st.header("📂 Upload Dataset")

    uploaded_file = st.file_uploader("Upload CSV / Excel", type=["csv", "xlsx"])

    if uploaded_file:
        uploaded_file.seek(0)
        df = st.session_state.agent.ingestion.ingest_from_url(None, file_obj=uploaded_file)

        st.session_state.data_state["df"] = df
        st.session_state.agent.data_engine = DataPointEngine(df)
        st.session_state.data_state["kpis"] = []
        st.session_state.data_state["data_points"] = []
        st.session_state.data_state["insights"] = []

        st.success("Dataset loaded successfully")

# ---------------- PREVIEW ----------------
elif st.session_state.page == "Preview":
    st.header("🔍 Dataset Preview")

    df = st.session_state.data_state["df"]
    if df is None:
        st.warning("Upload dataset first")
    else:
        st.subheader("📊 Numeric Dataset Statistics")
        numeric_df = df.select_dtypes(include="number")
        if not numeric_df.empty:
            st.dataframe(numeric_df.describe().transpose(), use_container_width=True)

        st.subheader("🧩 Column Info")
        info_df = pd.DataFrame({
            "Column": df.columns,
            "Type": df.dtypes.astype(str),
            "Missing": df.isnull().sum().values
        })
        st.dataframe(info_df, use_container_width=True)

        st.subheader("🔎 Sample Data")
        st.dataframe(df.head(20), use_container_width=True)

# ---------------- CLEANING ----------------
elif st.session_state.page == "Cleaning":
    st.header("🧹 Data Cleaning")

    df = st.session_state.data_state["df"]
    if df is None:
        st.warning("Upload dataset first")
    else:
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        other_cols = [c for c in df.columns if c not in numeric_cols + categorical_cols]

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown("### Numeric")
            num_strategy = st.selectbox("Strategy", ["Mean", "Median", "Zero", "Drop rows"])
            st.caption(", ".join(numeric_cols))

        with c2:
            st.markdown("### Categorical")
            cat_strategy = st.selectbox("Strategy", ["Mode", "Unknown", "Drop rows"])
            st.caption(", ".join(categorical_cols))

        with c3:
            st.markdown("### Other")
            other_strategy = st.selectbox("Strategy", ["Drop rows", "Leave as is"])
            st.caption(", ".join(other_cols))

        if st.button("Apply Cleaning"):
            df_clean = df.copy()

            if numeric_cols:
                if num_strategy == "Mean":
                    df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].mean())
                elif num_strategy == "Median":
                    df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].median())
                elif num_strategy == "Zero":
                    df_clean[numeric_cols] = df_clean[numeric_cols].fillna(0)
                elif num_strategy == "Drop rows":
                    df_clean = df_clean.dropna(subset=numeric_cols)

            if categorical_cols:
                if cat_strategy == "Mode":
                    for col in categorical_cols:
                        df_clean[col] = df_clean[col].fillna(df_clean[col].mode()[0])
                elif cat_strategy == "Unknown":
                    df_clean[categorical_cols] = df_clean[categorical_cols].fillna("Unknown")
                elif cat_strategy == "Drop rows":
                    df_clean = df_clean.dropna(subset=categorical_cols)

            if other_cols and other_strategy == "Drop rows":
                df_clean = df_clean.dropna(subset=other_cols)

            st.session_state.data_state["df"] = df_clean
            st.session_state.agent.data_engine = DataPointEngine(df_clean)
            st.success("Cleaning applied")

# ---------------- DASHBOARD ----------------
elif st.session_state.page == "Dashboard":
    st.header("📊 KPI Dashboard")

    df = st.session_state.data_state["df"]
    if df is None:
        st.warning("Upload dataset first")
    else:
        # KPIs
        if not st.session_state.data_state["kpis"]:
            domain = st.session_state.agent.classifier.classify(df)
            kpis = st.session_state.agent.composer.generate_kpis(domain.domain, list(df.columns))
            st.session_state.data_state["kpis"] = kpis

        # DataPoints
        if not st.session_state.data_state["data_points"]:
            dps = st.session_state.agent.data_engine.generate_data_points(
                df, st.session_state.data_state["kpis"]
            )
            st.session_state.data_state["data_points"] = dps

        dps = st.session_state.data_state["data_points"]

        cols = st.columns(2)
        to_delete = []

        for i, dp in enumerate(dps):
            chart_df = pd.DataFrame(dp.data)

            with cols[i % 2]:
                # ✅ use metadata from DataPointEngine
                title = getattr(dp, "title", f"Chart {i+1}")
                chart_type_default = getattr(dp, "chart_type", "bar")
                x_label = getattr(dp, "x_label", "Category")
                y_label = getattr(dp, "y_label", "Value")

                st.subheader(title)

                chart_type = st.selectbox(
                    "Chart Type",
                    ["bar", "line", "pie", "scatter", "histogram"],
                    index=["bar","line","pie","scatter","histogram"].index(chart_type_default)
                    if chart_type_default in ["bar","line","pie","scatter","histogram"] else 0,
                    key=f"type_{i}"
                )

                fig = None

                if chart_type in ["bar", "line"] and "label" in chart_df.columns:
                    if chart_type == "bar":
                        fig = px.bar(
                            chart_df, x="label", y="value",
                            labels={"label": x_label, "value": y_label},
                            color="label", title=title
                        )
                    else:
                        fig = px.line(
                            chart_df, x="label", y="value",
                            labels={"label": x_label, "value": y_label},
                            markers=True, title=title
                        )

                elif chart_type == "pie" and "label" in chart_df.columns:
                    fig = px.pie(chart_df, names="label", values="value", title=title)

                elif chart_type == "scatter" and "x" in chart_df.columns:
                    fig = px.scatter(
                        chart_df, x="x", y="y",
                        labels={"x": x_label, "y": y_label},
                        title=title
                    )

                elif chart_type == "histogram" and "value" in chart_df.columns:
                    fig = px.histogram(
                        chart_df, x="value",
                        labels={"value": x_label},
                        title=title
                    )

                else:
                    st.warning("Unsupported chart format")
                    continue

                fig.update_layout(height=330)
                st.plotly_chart(fig, use_container_width=True)

                if st.button("🗑 Delete Graph", key=f"del_{i}"):
                    to_delete.append(i)

        for idx in sorted(to_delete, reverse=True):
            del st.session_state.data_state["data_points"][idx]

        # -------- Add Custom Graph --------
        st.divider()
        st.subheader("➕ Add Custom Graph")

        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        all_cols = df.columns.tolist()

        c1, c2, c3 = st.columns(3)
        with c1:
            new_y = st.selectbox("Y-axis (Metric)", numeric_cols)
        with c2:
            new_x = st.selectbox("X-axis (Category)", all_cols)
        with c3:
            new_type = st.selectbox("Chart Type", ["bar", "line", "pie"])

        if st.button("Add Graph"):
            grp = df.groupby(new_x)[new_y].sum().reset_index().head(12)
            data = [{"label": str(r[new_x]), "value": float(r[new_y])} for _, r in grp.iterrows()]

            new_dp = DataPoint(kpi_id=f"custom_{uuid.uuid4().hex[:6]}", data=data)
            new_dp.title = f"{new_y.replace('_',' ').title()} by {new_x.replace('_',' ').title()}"
            new_dp.chart_type = new_type
            new_dp.x_label = new_x.replace("_"," ").title()
            new_dp.y_label = new_y.replace("_"," ").title()

            st.session_state.data_state["data_points"].append(new_dp)
            st.success("Custom graph added")
            st.rerun()

# ---------------- INSIGHTS ----------------
elif st.session_state.page == "Insights":
    st.header("💡 Key Business Insights")

    if not st.session_state.data_state["insights"]:
        insights = []
        for dp in st.session_state.data_state["data_points"]:
            an = st.session_state.agent.analytics.analyze(None, dp)
            insights.append(an)
        st.session_state.data_state["insights"] = insights

    for i, ins in enumerate(st.session_state.data_state["insights"]):
        with st.container(border=True):
            st.markdown(f"### 📊 Insight {i+1}")
            st.markdown(f"**🧠 Summary:** {ins.summary_text}")
            st.markdown("**🔍 What we found:**")
            for pt in ins.insights:
                st.markdown(f"✅ {pt}")
            st.info("This insight helps stakeholders understand patterns and take action.")

# ---------------- CHAT WITH DATA ----------------
elif st.session_state.page == "Chat with Data":
    st.header("💬 Chat with Your Data")

    df = st.session_state.data_state["df"]
    if df is None:
        st.warning("Upload dataset first")
    else:
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        question = st.text_input("Ask a question about your dataset")

        if st.button("Ask"):
            with st.spinner("Thinking..."):
                answer = st.session_state.agent.analytics.chat_with_data(
                    question=question,
                    df=df
                )
                st.session_state.chat_history.append((question, answer))

        for q, a in reversed(st.session_state.chat_history):
            st.markdown(f"🧑 **You:** {q}")
            st.markdown(f"🤖 **DataBot:** {a}")
            st.divider()
