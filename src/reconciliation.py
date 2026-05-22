import json
import pandas as pd

from normalizer import normalize_dataframe

AMOUNT_TOLERANCE = 0.01


def load_data(internal_file, external_file):
    internal_df = pd.read_csv(internal_file);
    external_df = pd.read_csv(external_file);

    return internal_df, external_df

def is_amount_different(amount_internal, amount_external):
    if pd.isna(amount_internal) or pd.isna(amount_external):
        return True
    
    difference = abs(amount_external - amount_internal)

    return difference > AMOUNT_TOLERANCE

def calculate_amount_difference(amount_internal, amount_external):
    if pd.isna(amount_internal) or pd.isna(amount_external):
        return None
    
    return round(amount_external - amount_internal, 2)

def get_duplicated_operation_ids(df):
    operation_ids = df["operation_id"].dropna()

    duplicated_ids = operation_ids[operation_ids.duplicated(keep=False)]

    return set(duplicated_ids.unique())

def get_first_value(df, operation_id, column_name):
    rows = df[df["operation_id"] == operation_id]

    if rows.empty:
        return None
    
    if column_name not in rows.columns:
        return None
    
    value = rows.iloc[0][column_name]

    if pd.isna(value):
        return None
    
    return value

def build_duplicate_result(operation_id, internal_df, external_df):
    internal_rows = internal_df[internal_df["operation_id"] == operation_id]
    external_rows = external_df[external_df["operation_id"] == operation_id]

    internal_count = len(internal_rows)
    external_count = len(external_rows)

    status = []
    reasons = []

    if internal_count > 1:
        status.append("DUPLICATED_INTERNAL")
        reasons.append(f"Operation id {operation_id} appears {internal_count} times in internal source")

    if external_count > 1:
        status.append("DUPLICATED_EXTERNAL")
        reasons.append(f"Operation id {operation_id} appears {external_count} times in external source")

    return {
        "operation_id": operation_id,
        "status": status,
        "reason": reasons,
        "internal_amount": get_first_value(internal_df, operation_id, "amount"),
        "external_amount": get_first_value(external_df, operation_id, "amount"),
        "amount_difference": None,
        "internal_status": get_first_value(internal_df, operation_id, "status"),
        "external_status": get_first_value(external_df, operation_id, "status"),
        "internal_occurrences": internal_count,
        "external_occurrences": external_count,
        "has_difference": True,
        "difference_count": len(status),
    }



def build_duplicate_results(internal_df, external_df):
    duplicated_internal_ids = get_duplicated_operation_ids(internal_df)
    duplicated_external_ids = get_duplicated_operation_ids(external_df)

    duplicated_operation_ids = duplicated_internal_ids.union(duplicated_external_ids)

    duplicate_results = []

    for operation_id in sorted(duplicated_operation_ids):
        duplicate_results.append(
            build_duplicate_result(operation_id, internal_df, external_df)
        )

    return duplicate_results, duplicated_operation_ids



def verify_errors(row):

    if row["_merge"] == "left_only":
        return {
            "operation_id": row["operation_id"],
            "status": ["ONLY_INTERNAL"],
            "reason": ["Operation exists only in internal source"],
            "internal_amount": row.get("amount_internal"),
            "external_amount": None,
            "amount_difference": None,
            "internal_status": row.get("status_internal"),
            "external_status": None,
            "has_difference": True,
            "difference_count": 1,
            "internal_occurrences": 1,
            "external_occurrences": 0,
            }
    elif row["_merge"] == "right_only":
            return {
            "operation_id": row["operation_id"],
            "status": ["ONLY_EXTERNAL"],
            "reason": ["Operation exists only in external source"],
            "internal_amount": None,
            "external_amount": row.get("amount_external"),
            "amount_difference": None,
            "internal_status": None,
            "external_status": row.get("status_external"),
            "has_difference": True,
            "difference_count": 1,
            "internal_occurrences": 0,
            "external_occurrences": 1,
            }

    amount_internal = row["amount_internal"]
    amount_external = row["amount_external"]
    status_internal = row["status_internal"]
    status_external = row["status_external"]

    status = []
    reasons = []

    amount_difference = calculate_amount_difference(amount_internal, amount_external)

    if is_amount_different(amount_internal, amount_external):
        status.append("VALUE_MISMATCH")
        reasons.append("Amount is different between sources")

    if status_internal != status_external:
        status.append("STATUS_MISMATCH")
        reasons.append("Status is different between sources")



    if len(status) == 0:
        return {
        "operation_id": row["operation_id"],
        "status": ["MATCHED"],
        "reason": ["Operation matched successfully"],
        "internal_amount": amount_internal,
        "external_amount": amount_external,
        "amount_difference": amount_difference,
        "internal_status": status_internal,
        "external_status": status_external,
        "has_difference": False,
        "difference_count": 0,
        "internal_occurrences": 1,
        "external_occurrences": 1,
        }

  
    return {
        "operation_id": row["operation_id"],
        "status": status,
        "reason": reasons,
        "internal_amount": amount_internal,
        "external_amount": amount_external,
        "amount_difference": amount_difference,
        "internal_status": status_internal,
        "external_status": status_external,
        "has_difference": True,
        "difference_count": len(status),
        "internal_occurrences": 1,
        "external_occurrences": 1,
    }

def reconcile(internal_df, external_df):

    internal_df = normalize_dataframe(internal_df)
    external_df = normalize_dataframe(external_df)

    duplicate_results, duplicated_operation_ids = build_duplicate_results(
        internal_df,
        external_df
    )

    internal_without_duplicates = internal_df[
        internal_df["operation_id"].apply(lambda operation_id: not (operation_id in duplicated_operation_ids))
    ]

    external_without_duplicates = external_df[
        ~external_df["operation_id"].isin(duplicated_operation_ids)
    ]


    merged_df = internal_without_duplicates.merge(
        external_without_duplicates,
        on="operation_id",
        how="outer",
        suffixes=("_internal", "_external"),
        indicator=True
    )

    results = []

    for duplicate_result in duplicate_results:
        results.append(duplicate_result)

    for _, row in merged_df.iterrows():
        results.append(verify_errors(row))

    return pd.DataFrame(results)   



def build_summary(internal_df, external_df, result_df):
    status_mismatch = int(result_df["status"].apply(lambda status: "STATUS_MISMATCH" in status).sum())
    value_mismatch = int(result_df["status"].apply(lambda status: "VALUE_MISMATCH" in status).sum())
    matched = int(result_df["status"].apply(lambda status: "MATCHED" in status).sum())
    only_internal = int(result_df["status"].apply(lambda status: "ONLY_INTERNAL" in status).sum())
    only_external = int(result_df["status"].apply(lambda status: "ONLY_EXTERNAL" in status).sum())
    duplicated_internal = int(result_df["status"].apply(lambda status: "DUPLICATED_INTERNAL" in status).sum())
    duplicated_external = int(result_df["status"].apply(lambda status: "DUPLICATED_EXTERNAL" in status).sum())

    duplicated_records = int(
        result_df["status"].apply(
            lambda status: (
                "DUPLICATED_INTERNAL" in status
                or "DUPLICATED_EXTERNAL" in status
            )
        ).sum()
    )

    divergent_records = int(result_df["has_difference"].sum())

    summary = {
        "total_internal": len(internal_df),
        "total_external": len(external_df),
        "total_results": len(result_df),
        "matched": matched,
        "divergent_records": divergent_records,
        "status_mismatch": status_mismatch,
        "value_mismatch": value_mismatch,
        "only_internal": only_internal,
        "only_external": only_external,
        "duplicated_internal": duplicated_internal,
        "duplicated_external": duplicated_external,
        "duplicated_records": duplicated_records,
    }

    return summary

def save_outputs(result_df, summary, output_dir):
    output_dir.mkdir(exist_ok=True)

    differences_df = result_df[result_df["has_difference"] == True]

    matched_df = result_df[result_df["has_difference"] == False]

    matched_df.to_csv(output_dir / "matched.csv", index=False)

    differences_df.to_csv(output_dir / "differences.csv", index=False)

    with open(output_dir / "summary.json", "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4, ensure_ascii=False)

