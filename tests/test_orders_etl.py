# tests/test_orders_etl.py
import pandas as pd
import pytest
from src.etl.orders_etl import OrdersETL

@pytest.fixture
def orders_etl():
    etl = OrdersETL()
    # Monkeypatch DB fetch helper to return a controlled set
    etl._fetch_valid_user_ids = lambda: {1, 2, 3}
    etl.db_conn = None
    return etl

def test_orders_happy(orders_etl):
    df = pd.DataFrame([
        {"user_id": 1, "total_amount": 50},
        {"user_id": 2, "total_amount": 20}
    ])
    cleaned = orders_etl.clean_data(df)
    transformed = orders_etl.transform_data(cleaned)
    valid, invalid = orders_etl.validate_data(transformed)
    assert len(valid) == 2
    assert invalid.empty

def test_orders_invalid_user_and_amount(orders_etl):
    df = pd.DataFrame([
        {"user_id": 99, "total_amount": 10},    # invalid user
        {"user_id": 1, "total_amount": -5},     # negative amount
        {"user_id": None, "total_amount": 10}   # missing user
    ])
    cleaned = orders_etl.clean_data(df)
    transformed = orders_etl.transform_data(cleaned)
    valid, invalid = orders_etl.validate_data(transformed)
    assert len(valid) == 0
    assert len(invalid) >= 3