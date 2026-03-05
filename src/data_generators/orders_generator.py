"""
Orders data generator for the ecommerce platform.

This module generates realistic order records,
ensures user foreign key consistency,
maintains incremental IDs,
and injects controlled bad records.

Table Schema:
    orders (
        id SERIAL PRIMARY KEY,
        user_id INT REFERENCES users(id),
        total_amount NUMERIC(10,2),
        status VARCHAR(50) DEFAULT 'pending',
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


class OrdersGenerator(BaseGenerator):
    """
    Concrete generator for the `orders` table.

    Responsibilities:
        - Generate valid order records
        - Ensure valid foreign key user_id
        - Inject invalid records
        - Maintain incremental ID state
    """

    VALID_STATUSES = ["pending", "completed", "shipped", "cancelled"]

    def __init__(self, batch_size: int = 40) -> None:
        """
        Initialize OrdersGenerator.

        Args:
            batch_size (int): Number of orders per run.
        """
        super().__init__(entity_name="orders")

        self.batch_size = batch_size
        self.state_manager = StateManager()
        self.logger = get_logger(__name__)

    def generate_records(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Generate order records.

        Returns:
            Tuple[List[Dict], List[Dict]]:
                - Valid order records
                - Invalid order records
        """
        good_records: List[Dict] = []
        bad_records: List[Dict] = []

        # Load existing user IDs to maintain foreign key integrity
        user_ids = self._load_existing_user_ids()

        if not user_ids:
            self.logger.error("No users available. Cannot generate orders.")
            return good_records, bad_records

        last_id = self.state_manager.get_last_id("orders_last_id")

        self.logger.info(
            f"Generating {self.batch_size} orders starting from ID {last_id + 1}"
        )

        for i in range(self.batch_size):
            try:
                new_id = last_id + i + 1

                record = self._create_valid_order(new_id, user_ids)

                if self._should_inject_bad_record():
                    bad_record = self._create_invalid_order(new_id)
                    bad_records.append(bad_record)
                    continue

                good_records.append(record)

            except Exception:
                self.logger.exception("Error generating individual order record")
                continue

        # Update state safely
        if good_records:
            max_id_generated = good_records[-1]["id"]
            self.state_manager.update_last_id("orders_last_id", max_id_generated)

        return good_records, bad_records

    def _create_valid_order(self, order_id: int, user_ids: List[int]) -> Dict:
        """
        Create a valid order record.

        Args:
            order_id (int): ID to assign.
            user_ids (List[int]): Valid user IDs.

        Returns:
            Dict: Valid order record.
        """
        user_id = random.choice(user_ids)

        total_amount = self._generate_total_amount()

        status = random.choice(self.VALID_STATUSES)

        return {
            "id": order_id,
            "user_id": user_id,
            "total_amount": total_amount,
            "status": status,
            "created_at": datetime.utcnow().isoformat(),
        }

    def _create_invalid_order(self, order_id: int) -> Dict:
        """
        Create an intentionally invalid order record.

        Example invalid cases:
            - Non-existent user_id
            - Negative total_amount
            - Invalid status

        Args:
            order_id (int): ID to assign.

        Returns:
            Dict: Invalid order record.
        """
        return {
            "id": order_id,
            "user_id": -9999,  # Invalid foreign key
            "total_amount": Decimal("-100.00"),  # Invalid negative total
            "status": "unknown_status",  # Invalid status
            "created_at": datetime.utcnow().isoformat(),
        }

    def _load_existing_user_ids(self) -> List[int]:
        """
        Load user IDs from raw users CSV files.

        Returns:
            List[int]: List of valid user IDs.
        """
        user_dir = Path("data/raw/users")
        user_ids: List[int] = []

        if not user_dir.exists():
            return user_ids

        # Read all CSV files in users raw directory
        for file in user_dir.glob("*.csv"):
            try:
                with file.open("r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        user_ids.append(int(row["id"]))
            except Exception:
                self.logger.exception(f"Failed reading users file: {file}")

        return user_ids

    def _generate_total_amount(self) -> Decimal:
        """
        Generate order total respecting NUMERIC(10,2).

        Returns:
            Decimal: Total order amount.
        """
        raw_amount = Decimal(random.uniform(20, 1000))
        return raw_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def _should_inject_bad_record() -> bool:
        """
        Determine whether to inject a bad record.

        Returns:
            bool: True if bad record should be injected.
        """
        return random.random() < 0.05