import streamlit as st
from data_loader import load_data
from search_engine import search_fpr

st.set_page_config(page_title="FPR Analysis App", layout="wide")
st.title("🔍 FPR Analysis App")
st.markdown("Search the FPR database for potential failures, cause assessments and corrective actions.")

df = load_data()

# ---- Search Fields ----
st.markdown("### Search Fields")
st.markdown("*1 field = OR search | 2+ fields = AND search*")

col1, col2, col3, col4 = st.columns(4)
with col1:
    serial_no = st.text_input("Serial Number")
with col2:
    defective_part_no = st.text_input("Defective Part Number")
with col3:
    assembly_part_no = st.text_input("Assembly Part Number")
with col4:
    description = st.text_input("Failure Description")

# ---- Run Search ----
if serial_no or defective_part_no or assembly_part_no or description:
    results = search_fpr(df, serial_no, defective_part_no, assembly_part_no, description)
    if len(results) > 0:
        st.success(f"✅ Found **{len(results)}** potential failure match(es).")
    else:
        st.warning("⚠️ No matches found. Try a shorter search term.")
else:
    results = df
    st.info(f"ℹ️ Showing all **{len(df)}** records. Use the fields above to search.")

# ---- Replace NaN with "None" ----
results = results.fillna("None")

# ---- Style "None" as light grey in the table ----
def highlight_none(val):
    if str(val) == "None":
        return "color: lightgrey;"
    return ""

# Use .map() instead of .applymap() for pandas 2.0+
styled_results = results.style.map(highlight_none)

# ---- Main Results Table ----
st.dataframe(styled_results, use_container_width=True, hide_index=True)

# ---- Helper: display field with grey "None" ----
def display_field(label, value):
    if str(value) == "None":
        st.markdown(
            f"**{label}:** <span style='color:lightgrey'>None</span>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(f"**{label}:** {value}")

# ---- Sidebar: Row Detail Viewer ----
st.sidebar.header("📄 Row Detail Viewer")
st.sidebar.markdown("Select an FPR Number to view full details of that row.")

if len(results) > 0 and "FPR NUMBER" in results.columns:
    fpr_list = results["FPR NUMBER"].tolist()
    selected_fpr = st.sidebar.selectbox("Select FPR Number", fpr_list)

    if st.sidebar.button("🔍 Show Details"):
        row = results[results["FPR NUMBER"] == selected_fpr].iloc[0]

        st.markdown("---")
        st.markdown(f"## 📄 Details for FPR: `{selected_fpr}`")

        # Short value columns
        short_cols = ["FPR NUMBER", "SERIAL NUMBER", "DEFECTIVE PART NUMBER", "ASSEMBLY PART NUMBER"]

        # Long text columns
        long_cols = [
            col for col in results.columns
            if any(key in col for key in [
                "DESCRIPTION", "CAUSE", "ACTION", "CORRECTIVE", "RECOMMEND", "FOLLOW"
            ])
        ]

        # ---- Short fields ----
        st.markdown("### Key Fields")
        for col in short_cols:
            if col in results.columns:
                display_field(col, row[col])

        # ---- Long text fields in expanders ----
        st.markdown("### Full Text Fields")
        for col in long_cols:
            if col in results.columns:
                with st.expander(f"📝 {col}", expanded=True):
                    if str(row[col]) == "None":
                        st.markdown(
                            "<span style='color:lightgrey'>None</span>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.write(row[col])
else:
    st.sidebar.info("Run a search above to see results here.")
