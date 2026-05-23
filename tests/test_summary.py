from reconciliation import reconcile, build_summary
import pandas as pd

def test_should_count_matched_and_divergent_records():
    internal_df = pd.DataFrame([
        {
            "operation_id": "OP001",
            "amount": 100.00,
            "status": "SETTLED",
        },
        {
            "operation_id": "OP002",
            "amount": 200.00,
            "status": "SETTLED",
        },
    ])

    external_df = pd.DataFrame([
        {
            "operation_id": "OP001",
            "amount": 100.00,
            "status": "SETTLED",
        },
        {
            "operation_id": "OP002",
            "amount": 250.00,
            "status": "SETTLED",
        },
    ])

    result_df = reconcile(internal_df, external_df)
    summary = build_summary(internal_df, external_df, result_df)

    assert summary["total_internal"] == 2
    assert summary["total_external"] == 2
    assert summary["matched"] == 1
    assert summary["value_mismatch"] == 1
    assert summary["divergent_records"] == 1