def validate_csv(df):

    missing_fields = []

    if "amount" not in df.columns:
        missing_fields.append("amount")
    if "status" not in df.columns:
        missing_fields.append("status")
    if "operation_id" not in df.columns:
        missing_fields.append("operation_id")
    
    if len(missing_fields) > 0:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
