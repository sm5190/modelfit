import os

import httpx
import streamlit as st

API_BASE_URL = os.getenv("MODELFIT_API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="ModelFit", page_icon="⚖️", layout="wide")
st.title("ModelFit")
st.caption("Compare model behavior using transparent, task-specific evidence.")

with st.sidebar:
    st.header("Evaluation setup")
    task_type = st.selectbox(
        "Task type",
        ["summarization", "extraction", "email_writing", "code_generation"],
    )
    selected_models = st.multiselect(
        "Candidate models",
        ["phi_4_mini", "qwen3_8b", "gemma_3_12b", "qwen_2_5_vl"],
        default=["phi_4_mini", "qwen3_8b"],
    )

prompt = st.text_area(
    "Describe the task",
    height=180,
    placeholder="Example: Summarize this policy for a non-technical startup founder.",
)

if st.button("Run comparison", type="primary", use_container_width=True):
    if not prompt.strip():
        st.error("Enter a task before running the comparison.")
    elif len(selected_models) < 2:
        st.error("Select at least two candidate models.")
    else:
        try:
            response = httpx.post(
                f"{API_BASE_URL}/api/v1/runs",
                json={
                    "prompt": prompt,
                    "task_type": task_type,
                    "model_ids": selected_models,
                },
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()
            st.success(f"Evaluation queued. Run ID: {data['run_id']}")
            st.json(data)
        except httpx.HTTPError as exc:
            st.error(f"Could not reach the ModelFit API: {exc}")

st.divider()
st.subheader("Comparison results")
st.info("Candidate responses and evidence-backed scorecards will appear here.")
