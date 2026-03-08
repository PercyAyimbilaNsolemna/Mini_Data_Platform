# tests/test_products_etl.py
import pandas as pd
import pytest
from src.etl.products_etl import ProductsETL

@pytest.fixture
def products_etl():
    etl = ProductsETL()
    etl.db_conn = None
    return etl

def test_products_happy(products_etl):
    df = pd.DataFrame([
        {"name": "Laptop", "description": "Good", "price": "1200"},
        {"name": "Phone", "description": "Nice", "price": 300}
    ])
    cleaned = products_etl.clean_data(df)
    transformed = products_etl.transform_data(cleaned)
    valid, invalid = products_etl.validate_data(transformed)
    assert len(valid) == 2
    assert invalid.empty

def test_products_invalid_price(products_etl):
    df = pd.DataFrame([
        {"name": "Broken", "price": -5},
        {"name": None, "price": 10},
    ])
    cleaned = products_etl.clean_data(df)
    transformed = products_etl.transform_data(cleaned)
    valid, invalid = products_etl.validate_data(transformed)
    assert len(valid) == 0
    assert len(invalid) >= 2