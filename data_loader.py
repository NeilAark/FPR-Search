import pandas as pd

def load_data(filepath='FPR_Database.xlsx'):
    df = pd.read_excel(filepath, sheet_name='fpr_nmoniz')
    
    # Key columns we care about for search & display
    key_columns = [
        'FPR Number',
        'Assembly Part Number',
        'Defective Part Number',
        'Defective Part Number Description',
        'Serial Number',
        'Failure Description',
        'Cause Assessment',
        'Root Cause Category',
        'Corrective Action',
        'Follow-Up Action',
        'Status',
        'Incident Date',
        'Date Closed',
        'Customer',
        'Project',
        'Rig',
        'Division',
        'Segment',
        'Loss Category',
        'Dollar Loss',
        'Non Productive Time'
    ]
    
    # Keep only columns that exist in the file
    available_columns = [col for col in key_columns if col in df.columns]
    df = df[available_columns]
    
    # Drop rows with no failure description (essential for search)
    df = df.dropna(subset=['Failure Description'])
    df = df.fillna('Unknown')
    
    return df