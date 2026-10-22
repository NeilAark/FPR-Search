import numpy as np

def search_fpr(df, serial_no, defective_part_no, assembly_part_no, description):

    # Exact column names from your Excel sheet
    col_fpr         = "FPR NUMBER"
    col_serial      = "SERIAL NUMBER"
    col_defective   = "DEFECTIVE PART NUMBER"
    col_assembly    = "ASSEMBLY PART NUMBER"
    col_description = "FAILURE DESCRIPTION"

    # Columns to always exclude from results
    exclude_cols = {"ROOT CAUSE CATEGORY", "PENDING ACTION", "INVESTIGATION DETAILS"}

    # Collect only the filled fields
    queries = []
    if serial_no and serial_no.strip():
        queries.append((col_serial, serial_no.strip()))
    if defective_part_no and defective_part_no.strip():
        queries.append((col_defective, defective_part_no.strip()))
    if assembly_part_no and assembly_part_no.strip():
        queries.append((col_assembly, assembly_part_no.strip()))
    if description and description.strip():
        queries.append((col_description, description.strip()))

    # Nothing entered — return empty
    if not queries:
        return df.iloc[0:0]

    # 1 field filled = OR across all rows in that column
    # 2+ fields filled = AND — all filled fields must match
    if len(queries) == 1:
        col, val = queries[0]
        mask = df[col].str.contains(val, case=False, na=False)
    else:
        mask = np.ones(len(df), dtype=bool)
        for col, val in queries:
            mask &= df[col].str.contains(val, case=False, na=False)

    results = df[mask].copy()

    # Auto-detect cause, follow-up, action, corrective columns
    cause_cols      = [col for col in df.columns if "CAUSE" in col]
    follow_cols     = [col for col in df.columns if "FOLLOW" in col]
    action_cols     = [col for col in df.columns if "ACTION" in col]
    corrective_cols = [col for col in df.columns if "CORRECTIVE" in col or "RECOMMEND" in col]

    display_cols = (
        [col_fpr, col_serial, col_defective, col_assembly, col_description]
        + cause_cols + follow_cols + action_cols + corrective_cols
    )

    # Deduplicate while preserving order
    seen = set()
    display_cols = [c for c in display_cols if not (c in seen or seen.add(c))]

    # Remove excluded columns
    display_cols = [col for col in display_cols if col not in exclude_cols]

    # Only keep columns that actually exist in the DataFrame
    display_cols = [col for col in display_cols if col in df.columns]

    return results[display_cols]
