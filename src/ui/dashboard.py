import logging
import streamlit as st
from typing import Dict, Any

from ui.services.api_client import APIClient

# ----------------------------------------
# Logging
# ----------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("Dashboard")

# ----------------------------------------
# Config
# ----------------------------------------

API_BASE_URL = "http://localhost:8000"

client = APIClient(API_BASE_URL)

# ----------------------------------------
# UI Layout
# ----------------------------------------

st.set_page_config(
    page_title="📊 AI Market Intelligence",
    layout="wide",
)

st.title("📊 AI Market Intelligence Dashboard")

# ----------------------------------------
# Latest Prediction Section
# ----------------------------------------

st.subheader("📈 Live Market Prediction")

prediction: Dict[str, Any] | None = client.get_latest_prediction()

if prediction:
    col1, col2, col3 = st.columns(3)

    col1.metric("Symbol", prediction.get("symbol", "N/A"))
    col2.metric("Price", prediction.get("price", "N/A"))
    col3.metric("Recommendation", prediction.get("recommendation", "N/A"))

    st.write("Confidence:", prediction.get("confidence", "N/A"))
    st.write("Brokerage Cost:", prediction.get("brokerage_cost", "N/A"))
else:
    st.info("No prediction available yet.")

st.divider()

# ----------------------------------------
# RAG Query Section
# ----------------------------------------

st.subheader("🤖 Ask AI (RAG)")

query = st.text_input("Enter your financial question")

if st.button("Submit") and query:
    with st.spinner("Generating answer..."):
        response = client.query_rag(query)

        if response:
            st.success("AI Response")
            st.write(response.get("answer", "No answer returned"))
        else:
            st.error("Failed to get response from RAG service.")

st.divider()

# ----------------------------------------
# Auto Refresh
# ----------------------------------------

st.caption("Auto-refresh every 10 seconds")
st.experimental_rerun()