# src/data_quality/validation_rules.py
"""
Validation rule constants used by entity ETLs.
"""

USER_USERNAME_REGEX = r"^[A-Za-z0-9_]{3,50}$"

PRODUCT_NAME_REGEX = r"^[A-Za-z0-9\s\-\_]{1,100}$"