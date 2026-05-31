import pandas as pd
from psycopg2.extras import Json

from database import get_connection

def to_database_value(value):
    if isinstance(value, list):
        return value
    
    if pd.isna(value):
        return None
    
    return value

def ensure_list(value):
    if isinstance(value, list):
        return value
    
    if pd.isna(value):
        return []
    
    return [value]

def save_reconciliation_to_database(run, summary, result_df):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            save_run(cursor, run, summary)
            save_results(cursor, run["run_id"], result_df)
            save_issues(cursor, run["run_id"], result_df)


def save_run(cursor, run, summary):
    cursor.execute(
        """
        INSERT INTO reconciliation_runs (
            run_id,
            status,
            started_at,
            finished_at,
            internal_file,
            external_file,
            output_path,
            summary
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            run["run_id"],
            run["status"],
            run["started_at"],
            run["finished_at"],
            run["internal_file"],
            run["external_file"],
            run.get("output_path"),
            Json(summary),
        ),
    )

def save_results(cursor, run_id, result_df):
    for _, row in result_df.iterrows():
        cursor.execute(
            """
            INSERT INTO reconciliation_results (
                run_id,
                operation_id,
                has_difference,
                difference_count,
                internal_amount,
                external_amount,
                amount_difference,
                internal_status,
                external_status,
                internal_date,
                external_date,
                internal_occurrences,
                external_occurrences
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                run_id,
                to_database_value(row.get("operation_id")),
                bool(row.get("has_difference")),
                int(row.get("difference_count")),
                to_database_value(row.get("internal_amount")),
                to_database_value(row.get("external_amount")),
                to_database_value(row.get("amount_difference")),
                to_database_value(row.get("internal_status")),
                to_database_value(row.get("external_status")),
                to_database_value(row.get("internal_date")),
                to_database_value(row.get("external_date")),
                to_database_value(row.get("internal_occurrences")),
                to_database_value(row.get("external_occurrences")),
            ),
        )


def save_issues(cursor, run_id, result_df):
    for _, row in result_df.iterrows():
        operation_id = to_database_value(row.get("operation_id"))
        statuses = ensure_list(row.get("status"))
        reasons = ensure_list(row.get("reason"))

        for index, issue_type in enumerate(statuses):
            if issue_type == "MATCHED":
                continue

            reason = reasons[index] if index < len(reasons) else None

            cursor.execute(
                """
                INSERT INTO reconciliation_issues (
                    run_id,
                    operation_id,
                    issue_type,
                    reason
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    run_id,
                    operation_id,
                    issue_type,
                    reason,
                ),
            )