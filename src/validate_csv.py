def validate_csv(df):
    required_fields = ["amount", "status", "amount", "operation_id", "date"]
    missing_fields = []

    for field in required_fields:
        if field not in df.columns:
            missing_fields.append(field)

    if len(missing_fields) > 0:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
