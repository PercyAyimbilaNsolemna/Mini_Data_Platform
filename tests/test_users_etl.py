# tests/test_users_etl.py
import pandas as pd
import pytest
from src.etl.users_etl import UsersETL

@pytest.fixture
def users_etl():
    # Create ETL and override DB connection to avoid real DB calls in tests
    etl = UsersETL()
    etl.db_conn = None  # ensure load_to_postgres is not called in validation tests
    return etl

def test_users_clean_transform_validate_happy(users_etl):
    df = pd.DataFrame([
        {"username": " Alice ", "email": "Alice@Example.COM"},
        {"username": "bob", "email": "bob@example.com"}
    ])
    cleaned = users_etl.clean_data(df)
    transformed = users_etl.transform_data(cleaned)
    valid, invalid = users_etl.validate_data(transformed)
    assert len(valid) == 2
    assert invalid.empty

def test_users_invalid_cases(users_etl):
    df = pd.DataFrame([
        {"username": "", "email": "no_name@example.com"},         # missing username
        {"username": "charlie", "email": "bad-email-format"},    # invalid email
        {"username": "dave", "email": None},                     # missing email
    ])
    cleaned = users_etl.clean_data(df)
    transformed = users_etl.transform_data(cleaned)
    valid, invalid = users_etl.validate_data(transformed)
    assert len(valid) == 0
    assert len(invalid) == 3

def test_users_duplicate_detection(users_etl):
    df = pd.DataFrame([
        {"username": "eve", "email": "eve@example.com"},
        {"username": "EVE ", "email": "eve@example.com"},  # duplicate after trim/lower
    ])
    cleaned = users_etl.clean_data(df)
    # duplicates removed during clean_data -> should be only 1 row left
    assert len(cleaned) == 1