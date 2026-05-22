import pandas as pd

STATUS_MAP = {
    "settled": "SETTLED",
    "liquidada": "SETTLED",
    "liquidado": "SETTLED",
    "completed": "SETTLED",
    "completo": "SETTLED",

    "pending": "PENDING",
    "pendente": "PENDING",

    "cancelled": "CANCELLED",
    "canceled": "CANCELLED",
    "cancelada": "CANCELLED",
    "cancelado": "CANCELLED",
}

def normalize_operation_id(value):
    if pd.isna(value):
        return value
    
    return str(value).strip().upper()

def normalize_status(value):
    if pd.isna(value):
        return value
    
    clean_value = str(value).strip().lower()

    return STATUS_MAP.get(clean_value, clean_value.upper())

def normalize_amount(value):
    if pd.isna(value):
        return value
    
    if isinstance(value, int) or isinstance(value, float):
        return float(value)
    
    clean_value = str(value).strip()

    clean_value = clean_value.replace("R$", "")
    clean_value = clean_value.replace(" ", "")

    if "," in clean_value and "." in clean_value:
        clean_value = clean_value.replace(".", "")
        clean_value = clean_value.replace(",", ".")
    else:
        clean_value = clean_value.replace(",",".")

    return float(clean_value)

def normalize_dataframe(df):
    normalized_df = df.copy()

    if "operation_id" in normalized_df.columns:
        normalized_df["operation_id"] = normalized_df["operation_id"].apply(normalize_operation_id)
    
    if "status" in normalized_df.columns:
        normalized_df["status"] = normalized_df["status"].apply(normalize_status)

    if "amount" in normalized_df.columns:
        normalized_df["amount"] = normalized_df["amount"].apply(normalize_amount)

    return normalized_df