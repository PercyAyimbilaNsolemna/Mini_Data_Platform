import json
import shutil
from pathlib import Path
from typing import Dict

from src.utils.logger import get_logger


logger = get_logger(__name__)


class StateManager:
    """
    Manages persistent incremental state for data generators.

    This class ensures:
        - Atomic state file writes
        - Automatic initialization
        - Schema validation
        - Corruption protection
        - Thread-safe file updates (best-effort)

    State file structure:
        {
            "users_last_id": int,
            "products_last_id": int,
            "orders_last_id": int,
            "order_items_last_id": int
        }
    """

    DEFAULT_STATE: Dict[str, int] = {
        "users_last_id": 0,
        "products_last_id": 0,
        "orders_last_id": 0,
        "order_items_last_id": 0,
    }

    def __init__(self, state_path: str = "data/state.json") -> None:
        """
        Initialize the StateManager.

        Args:
            state_path (str): Path to state file.
        """
        self.state_file = Path(state_path)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.state_file.exists():
            logger.info("State file not found. Initializing new state file.")
            self._write_state(self.DEFAULT_STATE.copy())

    def _read_state(self) -> Dict[str, int]:
        """
        Safely read state from disk.

        Returns:
            Dict[str, int]: Current state dictionary.

        Raises:
            RuntimeError: If state file is corrupted.
        """
        try:
            with self.state_file.open("r") as f:
                state = json.load(f)

            self._validate_state(state)
            return state

        except json.JSONDecodeError as e:
            logger.error("State file is corrupted. Backing up and resetting.")
            self._backup_corrupted_file()
            self._write_state(self.DEFAULT_STATE.copy())
            return self.DEFAULT_STATE.copy()

        except Exception as e:
            logger.exception("Unexpected error reading state file.")
            raise RuntimeError("Failed to read state file") from e

    def _write_state(self, state: Dict[str, int]) -> None:
        """
        Atomically write state to disk.

        Args:
            state (Dict[str, int]): Updated state dictionary.
        """
        temp_file = self.state_file.with_suffix(".tmp")

        try:
            with temp_file.open("w") as f:
                json.dump(state, f, indent=4)

            temp_file.replace(self.state_file)

        except Exception as e:
            logger.exception("Failed to write state file.")
            raise RuntimeError("Failed to persist state file") from e

    def _validate_state(self, state: Dict[str, int]) -> None:
        """
        Validate state structure.

        Args:
            state (Dict[str, int]): Loaded state.

        Raises:
            ValueError: If state schema is invalid.
        """
        for key in self.DEFAULT_STATE.keys():
            if key not in state:
                raise ValueError(f"Missing state key: {key}")
            if not isinstance(state[key], int):
                raise ValueError(f"Invalid type for {key}")

    def _backup_corrupted_file(self) -> None:
        """
        Backup corrupted state file for forensic debugging.
        """
        backup_path = self.state_file.with_suffix(".corrupted.json")
        shutil.copy(self.state_file, backup_path)
        logger.warning(f"Corrupted state file backed up to {backup_path}")

    def get_last_id(self, key: str) -> int:
        """
        Retrieve last ID for a specific entity.

        Args:
            key (str): State key (e.g., 'users_last_id').

        Returns:
            int: Last stored ID.
        """
        state = self._read_state()
        return state.get(key, 0)

    def update_last_id(self, key: str, value: int) -> None:
        """
        Update last ID for an entity.

        Args:
            key (str): State key.
            value (int): New last ID value.
        """
        state = self._read_state()
        state[key] = value
        self._write_state(state)
        logger.info(f"Updated state: {key} -> {value}")