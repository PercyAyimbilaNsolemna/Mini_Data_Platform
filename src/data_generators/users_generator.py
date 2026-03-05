"""
Users data generator for the ecommerce platform.

This module generates realistic user records using Faker,
maintains incremental IDs using StateManager,
and injects controlled bad records for data quality simulation.

Table Schema:
    users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
    )
"""

import random
from datetime import datetime
from typing import Dict, List, Tuple

from faker import Faker

from src.data_generators.base_generator import BaseGenerator
from src.utils.state_manager import StateManager
from src.utils.logger import get_logger


class UsersGenerator(BaseGenerator):
    """
    Concrete generator for the `users` table.

    Responsibilities:
        - Generate valid user records
        - Inject invalid records
        - Maintain incremental ID state
        - Ensure uniqueness constraints
    """

    def __init__(self, batch_size: int = 50) -> None:
        """
        Initialize UsersGenerator.

        Args:
            batch_size (int): Number of users to generate per run.
        """
        super().__init__(entity_name="users")

        self.batch_size = batch_size
        self.faker = Faker()
        self.state_manager = StateManager()
        self.logger = get_logger(__name__)

        # Maintain uniqueness within batch
        self._generated_usernames = set()
        self._generated_emails = set()

    def generate_records(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Generate user records.

        Returns:
            Tuple[List[Dict], List[Dict]]:
                - List of valid user records
                - List of invalid user records
        """
        good_records: List[Dict] = []
        bad_records: List[Dict] = []

        # Retrieve last ID from state
        last_id = self.state_manager.get_last_id("users_last_id")

        self.logger.info(f"Generating {self.batch_size} users starting from ID {last_id + 1}")

        for i in range(self.batch_size):
            try:
                # Increment ID manually (simulating SERIAL)
                new_id = last_id + i + 1

                record = self._create_valid_user(new_id)

                # Inject bad record with small probability
                if self._should_inject_bad_record():
                    bad_record = self._create_invalid_user(new_id)
                    bad_records.append(bad_record)
                    continue

                good_records.append(record)

            except Exception as e:
                # Catch per-record failures without crashing batch
                self.logger.exception("Error generating individual user record")
                continue

        # Update state only if generation succeeded
        if good_records:
            max_id_generated = good_records[-1]["id"]
            self.state_manager.update_last_id("users_last_id", max_id_generated)

        return good_records, bad_records

    def _create_valid_user(self, user_id: int) -> Dict:
        """
        Create a valid user record.

        Args:
            user_id (int): ID to assign.

        Returns:
            Dict: Valid user record.
        """
        # Generate unique username
        username = self._generate_unique_username()

        # Generate unique email
        email = self._generate_unique_email()

        return {
            "id": user_id,
            "username": username,
            "email": email,
            "created_at": datetime.utcnow().isoformat(),
        }

    def _create_invalid_user(self, user_id: int) -> Dict:
        """
        Create an intentionally invalid user record.

        Example invalid cases:
            - Missing email
            - Duplicate username
            - Empty username

        Args:
            user_id (int): ID to assign.

        Returns:
            Dict: Invalid user record.
        """
        return {
            "id": user_id,
            "username": "",  # Invalid: empty username
            "email": None,   # Invalid: null email
            "created_at": datetime.utcnow().isoformat(),
        }

    def _generate_unique_username(self) -> str:
        """
        Generate a unique username within current batch.

        Returns:
            str: Unique username.
        """
        while True:
            username = self.faker.user_name()
            if username not in self._generated_usernames:
                self._generated_usernames.add(username)
                return username

    def _generate_unique_email(self) -> str:
        """
        Generate a unique email within current batch.

        Returns:
            str: Unique email.
        """
        while True:
            email = self.faker.email()
            if email not in self._generated_emails:
                self._generated_emails.add(email)
                return email

    @staticmethod
    def _should_inject_bad_record() -> bool:
        """
        Randomly decide whether to inject a bad record.

        Returns:
            bool: True if bad record should be injected.
        """
        # 5% bad record rate
        return random.random() < 0.05