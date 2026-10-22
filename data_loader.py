import pandas as pd

def load_data():
    file_path = "FPR_Database.xlsx"
    df = pd.read_excel(file_path)

    # Clean column names
    df.columns = [str(col).strip().upper() for col in df.columns]

    # Fix duplicate column names
    counts = {}
    new_cols = []
    for col in df.columns:
        if col in counts:
            counts[col] += 1
            new_cols.append(f"{col}_{counts[col]}")
        else:
            counts[col] = 1
            new_cols.append(col)
    df.columns = new_cols

    # Convert the key columns to clean strings
    for col in ["SERIAL NUMBER", "DEFECTIVE PART NUMBER", "ASSEMBLY PART NUMBER", "FAILURE DESCRIPTION", "FPR NUMBER", "INVESTIGATION DETAILS"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()

    return df
