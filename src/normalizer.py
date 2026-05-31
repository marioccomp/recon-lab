import pandas as pd
import re

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
        return None
    
    clean_value = str(value).strip()

    if clean_value == "":
        return None
    
    return clean_value.upper()

def normalize_status(value):
    if pd.isna(value):
        return None
    
    clean_value = str(value).strip().lower()

    if clean_value == "":
        return None

    return STATUS_MAP.get(clean_value, clean_value.upper())

def normalize_amount(value):
    if pd.isna(value):
        return None
    
    if isinstance(value, int) or isinstance(value, float):
        return float(value)
    
    clean_value = str(value).strip()

    clean_value = clean_value.replace("R$", "")
    clean_value = clean_value.replace(" ", "")

    clean_value = re.sub(r"[^0-9.,-]", "", clean_value)

    if "," in clean_value and "." in clean_value:
        clean_value = clean_value.replace(".", "")
        clean_value = clean_value.replace(",", ".")
    else:
        clean_value = clean_value.replace(",",".")

    if clean_value == "":
        return None
    
    return float(clean_value)

def normalize_date(value):
    if pd.isna(value):
        return None
    
    value = str(value).strip()

    if value == "":
        return None
    
    if re.match(r"^\d{4}-\d{2}-\d{2}$", value):
        return value
    
    parsed_date = pd.to_datetime(value, dayfirst=True, errors="coerce")

    if pd.isna(parsed_date):
        return None
    
    return parsed_date.strftime("%Y-%m-%d")

def normalize_dataframe(df):
    normalized_df = df.copy()

    normalized_df["operation_id"] = normalized_df["operation_id"].apply(normalize_operation_id)

    normalized_df["status"] = normalized_df["status"].apply(normalize_status)

    normalized_df["amount"] = normalized_df["amount"].apply(normalize_amount)

    normalized_df["date"] = normalized_df["date"].apply(normalize_date)

    return normalized_df