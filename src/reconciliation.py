import json
from pathlib import Path

import pandas as pd


def load_data(internal_file, external_file):
    internal_df = pd.read_csv(internal_file);
    external_df = pd.read_csv(external_file);

    return internal_df, external_df

def verify_errors(row):

    if row["_merge"] == "left_only":
        return {
            "operation_id": row["operation_id"],
            "status": ["ONLY_INTERNAL"],
            "reason": "Operation exists only in internal source",
            "internal_amount": row.get("amount_internal"),
            "external_amount": None,
            "internal_status": row.get("status_internal"),
            "external_status": None
            }
    elif row["_merge"] == "right_only":
            return {
            "operation_id": row["operation_id"],
            "status": ["ONLY_EXTERNAL"],
            "reason": "Operation exists only in external source",
            "internal_amount": None,
            "external_amount": row.get("amount_external"),
            "internal_status": None,
            "external_status": row.get("status_external"),
            }

    amount_internal = row["amount_internal"]
    amount_external = row["amount_external"]
    status_internal = row["status_internal"]
    status_external = row["status_external"]

    status = []
    reasons = []

    if amount_external == amount_internal and status_internal == status_external:
        return {
        "operation_id": row["operation_id"],
        "status": ["MATCHED"],
        "reason": "Operation matched successfully",
        "internal_amount": amount_internal,
        "external_amount": amount_external,
        "internal_status": status_internal,
        "external_status": status_external,
        }

    if amount_external != amount_internal:
        status.append("VALUE_MISMATCH")
        reasons.append("Amount is different between sources")
    if status_internal != status_external:
        status.append("STATUS_MISMATCH")
        reasons.append("Status is different between sources")

    return {
        "operation_id": row["operation_id"],
        "status": status,
        "reason": reasons,
        "internal_amount": amount_internal,
        "external_amount": amount_external,
        "internal_status": status_internal,
        "external_status": status_external,
    }

def reconcile(internal_df, external_df):
    merged_df = internal_df.merge(
        external_df,
        on="operation_id",
        how="outer",
        suffixes=("_internal", "_external"),
        indicator=True
    )

    results = []

    for _, row in merged_df.iterrows():
        results.append(verify_errors(row))

    return pd.DataFrame(results)   



def build_summary(internal_df, external_df, result_df):
    status_mismatch = int(result_df["status"].apply(lambda status: "STATUS_MISMATCH" in status).sum())
    value_mismatch = int(result_df["status"].apply(lambda status: "VALUE_MISMATCH" in status).sum())
    matched = int(result_df["status"].apply(lambda status: "MATCHED" in status).sum())
    only_internal = int(result_df["status"].apply(lambda status: "ONLY_INTERNAL" in status).sum())
    only_external = int(result_df["status"].apply(lambda status: "ONLY_EXTERNAL" in status).sum())

    summary = {
        "total_internal": len(internal_df),
        "total_external": len(external_df),
        "total_results": len(result_df),
        "matched": matched,
        "status_mismatch": status_mismatch,
        "value_mismatch": value_mismatch,
        "only_internal": only_internal,
        "only_external": only_external
    }

    return summary

def save_outputs(result_df, summary, output_dir):
    output_dir.mkdir(exist_ok=True)

    differences_df = result_df[result_df["status"].apply(lambda status: "MATCHED" not in status)]

    matched_df = result_df[result_df["status"].apply(lambda status: "MATCHED" in status)]

    matched_df.to_csv(output_dir / "matched.csv", index=False)

    differences_df.to_csv(output_dir / "differences.csv", index=False)

    with open(output_dir / "summary.json", "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4, ensure_ascii=False)

