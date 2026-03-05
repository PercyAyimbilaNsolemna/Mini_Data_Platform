"""
Abstract base generator for all ecommerce data entities.

This class provides:
    - CSV file writing
    - Bad record segregation
    - Timestamp-based file naming
    - Directory auto-creation
    - Structured logging
    - Robust error handling

All entity-specific generators must inherit from this class.
"""

import csv
import datetime
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Tuple

from src.utils.logger import get_logger


class BaseGenerator(ABC):
    """
    Abstract base class for data generators.

    Subclasses must implement:
        - generate_records()

    This class handles:
        - Raw file writing
        - Bad record handling
        - Logging
        - Timestamp management
    """

    def __init__(self, entity_name: str) -> None:
        """
        Initialize generator.

        Args:
            entity_name (str): Name of the entity (e.g., 'users').
        """
        self.entity_name = entity_name
        self.raw_dir = Path(f"data/raw/{entity_name}")
        self.bad_dir = Path(f"data/bad_records/{entity_name}")

        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.bad_dir.mkdir(parents=True, exist_ok=True)

        self.logger = get_logger(f"{__name__}.{entity_name}")

    @abstractmethod
    def generate_records(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Generate good and bad records.

        Returns:
            Tuple[List[Dict], List[Dict]]:
                - List of valid records
                - List of invalid/bad records
        """
        pass

    def run(self) -> None:
        """
        Execute the generator workflow.

        This method:
            1. Generates records
            2. Writes valid records to raw folder
            3. Writes invalid records to bad_records folder
            4. Logs summary metrics
        """
        try:
            self.logger.info(f"Starting generation for {self.entity_name}")

            good_records, bad_records = self.generate_records()

            timestamp = self._current_timestamp()

            if good_records:
                self._write_csv(
                    records=good_records,
                    directory=self.raw_dir,
                    filename=f"{self.entity_name}_{timestamp}.csv",
                )

            if bad_records:
                self._write_csv(
                    records=bad_records,
                    directory=self.bad_dir,
                    filename=f"bad_{self.entity_name}_{timestamp}.csv",
                )

            self.logger.info(
                f"Completed {self.entity_name}: "
                f"{len(good_records)} valid, {len(bad_records)} invalid"
            )

        except Exception as e:
            self.logger.exception(
                f"Fatal error while generating {self.entity_name}"
            )
            raise

    def _write_csv(
        self,
        records: List[Dict],
        directory: Path,
        filename: str,
    ) -> None:
        """
        Write records to CSV file.

        Args:
            records (List[Dict]): Records to write.
            directory (Path): Target directory.
            filename (str): Output file name.
        """
        if not records:
            return

        file_path = directory / filename

        try:
            with file_path.open("w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(
                    csvfile,
                    fieldnames=records[0].keys(),
                )
                writer.writeheader()
                writer.writerows(records)

            self.logger.info(f"Wrote file: {file_path}")

        except Exception as e:
            self.logger.exception(f"Failed to write CSV file: {file_path}")
            raise

    @staticmethod
    def _current_timestamp() -> str:
        """
        Generate current UTC timestamp for file naming.

        Returns:
            str: Timestamp formatted as YYYYMMDD_HHMMSS
        """
        return datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")