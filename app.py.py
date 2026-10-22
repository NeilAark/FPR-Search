import streamlit as st
import pandas as pd
from data_loader import load_data
from search_engine import build_index, find_similar_failures

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FPR Failure Analysis Tool",
    page_icon="🔩",
    layout="wide"
)

# ─── Load & Index Data ─────────────────────────────────────────────────────────
@st.cache_resource
def initialise():
    df = load_data('FPR_Database.xlsx')
    embeddings = build_index(df)
    return df, embeddings

with st.spinner("📂 Loading FPR database and building search index..."):
    df, embeddings = initialise()

# ─── Header ────────────────────────────────────────────────────────────────────
st.title("🔩 FPR Failure Analysis Tool")
st.markdown(
    "Search the **Failure Problem Report (FPR) database** using a part number, "
    "serial number, and failure description to find similar historical cases and likely root causes."
)
st.caption(f"📊 Database loaded: **{len(df)} FPR records** available for search.")
st.divider()

# ─── Input Form ────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    assembly_part = st.text_input(
        "🔖 Assembly Part Number",
        placeholder="e.g. 2205443-06"
    )

with col2:
    defective_part = st.text_input(
        "⚙️ Defective Part Number",
        placeholder="e.g. 2205443-06"
    )

with col3:
    serial_number = st.text_input(
        "🔢 Serial Number",
        placeholder="e.g. 11060282-01"
    )

failure_description = st.text_area(
    "📝 Describe the Failure",
    placeholder=(
        "e.g. Leaking blowproof seals observed during subsea function test. "
        "Scratches found on seal face with O-ring debris in end cap..."
    ),
    height=130
)

col_a, col_b = st.columns([3, 1])
with col_a:
    num_results = st.slider("Number of similar FPR cases to retrieve", 1, 10, 5)
with col_b:
    st.write("")
    st.write("")
    search_clicked = st.button("🔍 Search FPR Database", type="primary", use_container_width=True)

# ─── Results ───────────────────────────────────────────────────────────────────
if search_clicked:
    if not failure_description.strip():
        st.warning("⚠️ Please enter a failure description to search.")
    else:
        query = (
            f"Assembly Part: {assembly_part}. "
            f"Defective Part: {defective_part}. "
            f"Serial Number: {serial_number}. "
            f"Failure: {failure_description}"
        )

        with st.spinner("🔎 Searching FPR database for similar failures..."):
            results = find_similar_failures(query, df, embeddings, top_k=num_results)

        st.divider()
        st.subheader(f"📋 Top {num_results} Similar FPR Cases Found")

        # ── Individual Case Cards ──────────────────────────────────────────────
        for rank, (_, row) in enumerate(results.iterrows(), start=1):
            score = row['Similarity %']

            if score >= 75:
                badge = "🟢"
                label = "High Match"
            elif score >= 50:
                badge = "🟡"
                label = "Moderate Match"
            else:
                badge = "🔴"
                label = "Low Match"

            fpr_num = row.get('FPR Number', 'N/A')
            short_desc = str(row.get('Failure Description', ''))[:70]

            with st.expander(
                f"{badge} #{rank} — FPR {fpr_num} | {score}% {label} | {short_desc}..."
            ):
                left, right = st.columns(2)

                with left:
                    st.markdown("#### 📌 Component Info")
                    st.markdown(f"**FPR Number:** {row.get('FPR Number', 'N/A')}")
                    st.markdown(f"**Assembly Part Number:** {row.get('Assembly Part Number', 'N/A')}")
                    st.markdown(f"**Defective Part Number:** {row.get('Defective Part Number', 'N/A')}")
                    st.markdown(f"**Defective Part Description:** {row.get('Defective Part Number Description', 'N/A')}")
                    st.markdown(f"**Serial Number:** {row.get('Serial Number', 'N/A')}")
                    st.divider()
                    st.markdown("#### 📅 Timeline & Status")
                    st.markdown(f"**Status:** {row.get('Status', 'N/A')}")
                    st.markdown(f"**Incident Date:** {row.get('Incident Date', 'N/A')}")
                    st.markdown(f"**Date Closed:** {row.get('Date Closed', 'N/A')}")
                    st.markdown(f"**Customer:** {row.get('Customer', 'N/A')}")
                    st.markdown(f"**Project:** {row.get('Project', 'N/A')}")
                    st.markdown(f"**Rig:** {row.get('Rig', 'N/A')}")

                with right:
                    st.markdown("#### 🔍 Failure Analysis")
                    st.markdown(f"**Failure Description:**\n\n{row.get('Failure Description', 'N/A')}")
                    st.divider()
                    st.markdown(f"**Cause Assessment:**\n\n{row.get('Cause Assessment', 'N/A')}")
                    st.divider()
                    st.markdown(f"**Root Cause Category:** {row.get('Root Cause Category', 'N/A')}")
                    st.divider()
                    st.markdown(f"**Corrective Action:**\n\n{row.get('Corrective Action', 'N/A')}")
                    st.divider()
                    st.markdown(f"**Follow-Up Action:**\n\n{row.get('Follow-Up Action', 'N/A')}")

                st.divider()
                loss_col1, loss_col2, loss_col3 = st.columns(3)
                with loss_col1:
                    st.metric("Loss Category", row.get('Loss Category', 'N/A'))
                with loss_col2:
                    st.metric("Dollar Loss", row.get('Dollar Loss', 'N/A'))
                with loss_col3:
                    st.metric("Non-Productive Time", row.get('Non Productive Time', 'N/A'))

        # ── AI Summary ────────────────────────────────────────────────────────
        st.divider()
        st.subheader("🤖 AI Root Cause Summary")
        st.markdown("Based on the retrieved FPR cases, here are the most frequently identified root causes:")

        col_rc1, col_rc2 = st.columns(2)

        with col_rc1:
            st.markdown("**🔴 Root Cause Categories:**")
            root_causes = results['Root Cause Category'].value_counts()
            for cause, count in root_causes.items():
                if cause != 'Unknown':
                    st.markdown(f"- **{cause}** — {count} similar case(s)")

        with col_rc2:
            st.markdown("**🔧 Suggested Corrective Actions (from similar cases):**")
            for idx, (_, row) in enumerate(results.iterrows(), 1):
                action = row.get('Corrective Action', 'N/A')
                if action not in ['Unknown', 'N/A']:
                    st.markdown(f"_{idx}. {action[:150]}..._")

        st.divider()
        st.info(
            "💡 **Want full AI-generated summaries?** "
            "An OpenAI or Azure OpenAI API key can be added to generate a written diagnostic "
            "report from the above cases. Ask Hugh about Azure OpenAI access within SLB."
        )