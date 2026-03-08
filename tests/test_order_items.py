# tests/test_order_items_etl.py
import pandas as pd
import pytest
from src.etl.order_items_etl import OrderItemsETL

@pytest.fixture
def order_items_etl():
    etl = OrderItemsETL()
    # Provide controlled valid ids
    etl._fetch_valid_order_ids = lambda: {10, 11}
    etl._fetch_valid_product_ids = lambda: {100, 101}
    etl.db_conn = None
    return etl

def test_order_items_happy(order_items_etl):
    df = pd.DataFrame([
        {"order_id": 10, "product_id": 100, "quantity": 2, "price": 20},
        {"order_id": 11, "product_id": 101, "quantity": 1, "price": 10}
    ])
    cleaned = order_items_etl.clean_data(df)
    transformed = order_items_etl.transform_data(cleaned)
    valid, invalid = order_items_etl.validate_data(transformed)
    assert len(valid) == 2
    assert invalid.empty

def test_order_items_invalids(order_items_etl):
    df = pd.DataFrame([
        {"order_id": 999, "product_id": 100, "quantity": 1, "price": 10},   # bad order_id
        {"order_id": 10, "product_id": 999, "quantity": 1, "price": 10},    # bad product_id
        {"order_id": 10, "product_id": 100, "quantity": 0, "price": 10},    # invalid quantity
        {"order_id": None, "product_id": 100, "quantity": 1, "price": 10}   # missing order_id
    ])
    cleaned = order_items_etl.clean_data(df)
    transformed = order_items_etl.transform_data(cleaned)
    valid, invalid = order_items_etl.validate_data(transformed)
    assert len(valid) == 0
    assert len(invalid) >= 4