"""
Products data generator for the ecommerce platform.

This module generates realistic product records using Faker,
maintains incremental IDs using StateManager,
and injects controlled bad records for data quality simulation.

Table Schema:
    products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        price NUMERIC(10,2) NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
    )
"""

import random
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Tuple

from faker import Faker

from src.data_generators.base_generator import BaseGenerator
from src.utils.state_manager import StateManager
from src.utils.logger import get_logger


class ProductsGenerator(BaseGenerator):
    """
    Concrete generator for the `products` table.

    Responsibilities:
        - Generate valid product records
        - Inject invalid records
        - Maintain incremental ID state
        - Respect NUMERIC precision requirements
    """

    def __init__(self, batch_size: int = 20) -> None:
        """
        Initialize ProductsGenerator.

        Args:
            batch_size (int): Number of products to generate per run.
        """
        super().__init__(entity_name="products")

        self.batch_size = batch_size
        self.faker = Faker()
        self.state_manager = StateManager()
        self.logger = get_logger(__name__)

    def generate_records(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Generate product records.

        Returns:
            Tuple[List[Dict], List[Dict]]:
                - List of valid product records
                - List of invalid product records
        """
        good_records: List[Dict] = []
        bad_records: List[Dict] = []

        # Retrieve last product ID from persistent state
        last_id = self.state_manager.get_last_id("products_last_id")

        self.logger.info(
            f"Generating {self.batch_size} products starting from ID {last_id + 1}"
        )

        for i in range(self.batch_size):
            try:
                # Simulate SERIAL behavior
                new_id = last_id + i + 1

                record = self._create_valid_product(new_id)

                # Inject bad record with small probability
                if self._should_inject_bad_record():
                    bad_record = self._create_invalid_product(new_id)
                    bad_records.append(bad_record)
                    continue

                good_records.append(record)

            except Exception:
                # Prevent single-record failure from killing batch
                self.logger.exception("Error generating individual product record")
                continue

        # Update state if at least one valid record generated
        if good_records:
            max_id_generated = good_records[-1]["id"]
            self.state_manager.update_last_id("products_last_id", max_id_generated)

        return good_records, bad_records

    def _create_valid_product(self, product_id: int) -> Dict:
        """
        Create a valid product record.

        Args:
            product_id (int): ID to assign.

        Returns:
            Dict: Valid product record.
        """
        # Generate realistic product name
        product_name = f"{self.faker.word().capitalize()} {self.faker.word().capitalize()}"

        # Generate description text
        description = self.faker.sentence(nb_words=12)

        # Generate price with correct decimal precision
        price = self._generate_price()

        return {
            "id": product_id,
            "name": product_name,
            "description": description,
            "price": price,
            "created_at": datetime.utcnow().isoformat(),
        }

    def _create_invalid_product(self, product_id: int) -> Dict:
        """
        Create an intentionally invalid product record.

        Example invalid cases:
            - Negative price
            - Missing name
            - Null price

        Args:
            product_id (int): ID to assign.

        Returns:
            Dict: Invalid product record.
        """
        return {
            "id": product_id,
            "name": None,  # Invalid: name cannot be NULL
            "description": self.faker.text(),
            "price": Decimal("-10.00"),  # Invalid: negative price
            "created_at": datetime.utcnow().isoformat(),
        }

    def _generate_price(self) -> Decimal:
        """
        Generate a price respecting NUMERIC(10,2) precision.

        Returns:
            Decimal: Price value rounded to 2 decimal places.
        """
        raw_price = Decimal(random.uniform(5, 500))
        return raw_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def _should_inject_bad_record() -> bool:
        """
        Determine whether to inject a bad record.

        Returns:
            bool: True if bad record should be injected.
        """
        # 5% bad record rate
        return random.random() < 0.05