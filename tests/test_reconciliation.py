import sys 
from pathlib import Path

import pandas as pd

from normalizer import normalize_status, normalize_amount
from reconciliation import reconcile

def test_should_normalize_status_and_amount():
    status = normalize_status(" liquidada  ")
    amount = normalize_amount(" R$ 1.000,50 ")

    assert status == "SETTLED"
    assert amount == 1000.50

def test_should_identify_value_mismatch():
    internal_df = pd.DataFrame([
        {
            "operation_id": "OP001",
            "amount": 100.00,
            "status": "SETTLED"
        }
    ])

    external_df = pd.DataFrame([
        {
            "operation_id": "OP001",
            "amount": 100.50,
            "status": "liquidado"
        }
    ])

    result_df = reconcile(internal_df, external_df)
    row = result_df.iloc[0]
    assert "VALUE_MISMATCH" in row["status"]
    assert bool(row["has_difference"]) is True
    assert row["amount_difference"] == 0.50

def test_should_identify_duplicated_operations():
    internal_df = pd.DataFrame([
        {
            "operation_id": "OP001",
            "amount": 100.00,
            "status": "SETTLED"
        },
        {
            "operation_id": "OP001",
            "amount": 150.00,
            "status": "SETTLED"
        }
    ])

    external_df = pd.DataFrame([
        {
            "operation_id": "OP001",
            "amount": 100.50,
            "status": "liquidado"
        }
    ])

    result_df = reconcile(internal_df, external_df)
    row = result_df.iloc[0]
    assert "DUPLICATED_INTERNAL" in row["status"]
    assert bool(row["has_difference"]) is True
    assert row["internal_occurrences"] == 2

def test_should_identify_matched_operation():
    internal_df = pd.DataFrame([
        {
            "operation_id": "OP001",
            "amount": 1050.00,
            "status": "pendente"
        }
    ])

    external_df = pd.DataFrame([
        {
            "operation_id": "  op001",
            "amount": "R$ 1050,00",
            "status": "pending"
        }
    ])

    result_df = reconcile(internal_df, external_df)

    row = result_df.iloc[0]

    assert "MATCHED" in row["status"]
    assert row["external_status"] == "PENDING"
    assert row["amount_difference"] == 0.0

def test_should_identify_status_mismatch():
    internal_df = pd.DataFrame([
        {
            "operation_id": "OP004",
            "amount": 10500,
            "status": "liquidada"
        }
    ])

    external_df = pd.DataFrame([
        {
            "operation_id": "OP004",
            "amount": 10500,
            "status": "pending"
        }
    ])

    result_df = reconcile(internal_df, external_df)

    row = result_df.iloc[0]

    assert "STATUS_MISMATCH" in row["status"]
    assert bool(row["has_difference"]) is True
    assert row["difference_count"] == 1


def test_should_identify_only_internal_operation():
    internal_df = pd.DataFrame([
        {
            "operation_id": "OP004",
            "amount": 10500,
            "status": "liquidada"
        },
        {
            "operation_id": "OP005",
            "amount": 10500,
            "status": "pending"
        }
    ])

    external_df = pd.DataFrame([
        {
            "operation_id": "OP004",
            "amount": 10500,
            "status": "pending"
        }
    ])

    result_df = reconcile(internal_df, external_df)

    row = result_df[result_df["operation_id"] == "OP005"].iloc[0]

    assert "ONLY_INTERNAL" in row["status"]
    assert bool(row["has_difference"]) is True
    assert row["difference_count"] == 1

def test_should_identify_only_external_operation():
    internal_df = pd.DataFrame([
        {
            "operation_id": "OP004",
            "amount": 10500,
            "status": "liquidada"
        },
        
    ])

    external_df = pd.DataFrame([
        {
            "operation_id": "OP004",
            "amount": 10500,
            "status": "pending"
        },
        {
            "operation_id": "OP005",
            "amount": 10500,
            "status": "pending"
        }
    ])

    result_df = reconcile(internal_df, external_df)

    row = result_df[result_df["operation_id"] == "OP005"].iloc[0]

    assert "ONLY_EXTERNAL" in row["status"] 
    assert bool(row["has_difference"]) is True
    assert row["difference_count"] == 1

def test_should_identify_value_and_status_mismatch():
    internal_df = pd.DataFrame([
        {
            "operation_id": "OP001",
            "amount": "R$ 1.000,50",
            "status": " liquidada"
        }
    ])

    external_df = pd.DataFrame([
        {
            "operation_id": "OP001",
            "amount": "2500",
            "status": "pendente"
        },
        {
            "operation_id": "OP002",
            "amount": "2400",
            "status": "pendente"
        }
    ])

    result_df = reconcile(internal_df, external_df)

    row = result_df[result_df["operation_id"] == "OP001"].iloc[0]
    row_only = result_df[result_df["operation_id"] == "OP002"].iloc[0]

    assert "VALUE_MISMATCH" in row["status"]
    assert "STATUS_MISMATCH" in row["status"]
    assert "ONLY_EXTERNAL" in row_only["status"]


