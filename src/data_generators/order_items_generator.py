"""
Order Items data generator for the ecommerce platform.

This module generates realistic order item records,
ensures foreign key integrity with orders and products,
maintains incremental IDs,
and injects controlled bad records for testing.

Table Schema:
    order_items (
        id SERIAL PRIMARY KEY,
        order_id INT REFERENCES orders(id),
        product_id INT REFERENCES products(id),
        quantity INT NOT NULL,
        price NUMERIC(10,2) NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
    )
"""

import csv
import random
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Dict, List, Tuple

from src.data_generators.base_generator import BaseGenerator
from src.utils.state_manager import StateManager
from src.utils.logger import get_logger


class OrderItemsGenerator(BaseGenerator):
    """
    Concrete generator for the `order_items` table.

    Responsibilities:
        - Generate valid order item records
        - Maintain foreign key integrity
        - Inject invalid records
        - Maintain incremental ID state
    """

    def __init__(self, batch_size: int = 80) -> None:
        """
        Initialize OrderItemsGenerator.

        Args:
            batch_size (int): Number of order items per run.
        """
        super().__init__(entity_name="order_items")

        self.batch_size = batch_size
        self.state_manager = StateManager()
        self.logger = get_logger(__name__)

    def generate_records(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Generate order item records.

        Returns:
            Tuple[List[Dict], List[Dict]]:
                - Valid records
                - Invalid records
        """
        good_records: List[Dict] = []
        bad_records: List[Dict] = []

        # Load dependencies from raw storage
        order_ids = self._load_ids_from_csv("data/raw/orders")
        product_ids = self._load_ids_from_csv("data/raw/products")

        # If no dependencies exist, we cannot proceed
        if not order_ids or not product_ids:
            self.logger.error(
                "Orders or Products not found. Cannot generate order_items."
            )
            return good_records, bad_records

        # Retrieve last incremental ID
        last_id = self.state_manager.get_last_id("order_items_last_id")

        self.logger.info(
            f"Generating {self.batch_size} order_items starting from ID {last_id + 1}"
        )

        for i in range(self.batch_size):
            try:
                # Simulate SERIAL behavior
                new_id = last_id + i + 1

                # Create valid record
                record = self._create_valid_order_item(
                    new_id,
                    order_ids,
                    product_ids,
                )

                # Inject invalid record with small probability
                if self._should_inject_bad_record():
                    bad_record = self._create_invalid_order_item(new_id)
                    bad_records.append(bad_record)
                    continue

                good_records.append(record)

            except Exception:
                # Prevent single-record failure from crashing batch
                self.logger.exception("Error generating individual order_item record")
                continue

        # Update state safely
        if good_records:
            max_id_generated = good_records[-1]["id"]
            self.state_manager.update_last_id(
                "order_items_last_id",
                max_id_generated,
            )

        return good_records, bad_records

    def _create_valid_order_item(
        self,
        item_id: int,
        order_ids: List[int],
        product_ids: List[int],
    ) -> Dict:
        """
        Create a valid order item record.

        Args:
            item_id (int): ID to assign.
            order_ids (List[int]): Valid order IDs.
            product_ids (List[int]): Valid product IDs.

        Returns:
            Dict: Valid order item record.
        """

        # Randomly assign existing order
        order_id = random.choice(order_ids)

        # Randomly assign existing product
        product_id = random.choice(product_ids)

        # Generate realistic quantity (minimum 1)
        quantity = random.randint(1, 5)

        # Generate realistic product price
        price = self._generate_price()

        return {
            "id": item_id,
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity,
            "price": price,
            "created_at": datetime.utcnow().isoformat(),
        }

    def _create_invalid_order_item(self, item_id: int) -> Dict:
        """
        Create an intentionally invalid order item record.

        Example invalid cases:
            - Non-existent foreign keys
            - Negative quantity
            - Negative price
        """
        return {
            "id": item_id,
            "order_id": -1,  # Invalid FK
            "product_id": -1,  # Invalid FK
            "quantity": -5,  # Invalid negative quantity
            "price": Decimal("-20.00"),  # Invalid negative price
            "created_at": datetime.utcnow().isoformat(),
        }

    def _load_ids_from_csv(self, directory_path: str) -> List[int]:
        """
        Load ID values from CSV files in a directory.

        Args:
            directory_path (str): Path to raw directory.

        Returns:
            List[int]: Extracted IDs.
        """
        directory = Path(directory_path)
        ids: List[int] = []

        if not directory.exists():
            return ids

        # Iterate through all CSV files in the directory
        for file in directory.glob("*.csv"):
            try:
                with file.open("r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        ids.append(int(row["id"]))
            except Exception:
                self.logger.exception(f"Failed reading file: {file}")

        return ids

    def _generate_price(self) -> Decimal:
        """
        Generate price respecting NUMERIC(10,2) precision.

        Returns:
            Decimal: Price value rounded to 2 decimal places.
        """
        raw_price = Decimal(random.uniform(5, 300))
        return raw_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def _should_inject_bad_record() -> bool:
        """
        Determine whether to inject a bad record.

        Returns:
            bool: True if bad record should be injected.
        """
        return random.random() < 0.05  # 5% bad record rate