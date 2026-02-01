"""
Load training data.
"""

import json
import random
from functools import lru_cache
from pathlib import Path

from meridian.config.settings import settings
from meridian.training.models import EntityAnnotation, TrainingItem


def _parse_item(raw: dict) -> TrainingItem:
    """
    Parse a raw JSON item into a TrainingItem.
    """
    return TrainingItem(
        text=raw["text"],
        entities=[
            EntityAnnotation(start=e[0], end=e[1], label=e[2]) for e in raw["entities"]
        ],
    )


@lru_cache(maxsize=1)
def load_default_data() -> list[TrainingItem]:
    """
    Load training data from the package default train.json.

    Result is cached.
    """
    return load_data(settings.TRAINING_DATA_DIR / settings.TRAINING_DATA_FILE)


def load_data(file_path: Path) -> list[TrainingItem]:
    """
    Load training data from a JSON file.

    Args:
        file_path: Path to the JSON data file.

    Returns:
        List of validated TrainingItem models.
    """
    with open(file_path, encoding="utf-8") as f:
        raw = json.load(f)
    return [_parse_item(item) for item in raw]


def split_data(
    data: list[TrainingItem],
    split_ratio: float = 0.2,
    seed: int | None = None,
) -> tuple[list[TrainingItem], list[TrainingItem]]:
    """
    Split data into training and validation sets.

    Args:
        data: All training data.
        split_ratio: Fraction of data for validation (0.0 to 1.0).
        seed: Random seed for reproducibility. Defaults to settings.

    Returns:
        Tuple of (train_data, valid_data).
    """
    seed = seed if seed is not None else settings.TRAINING_SEED
    shuffled = data.copy()
    random.seed(seed)
    random.shuffle(shuffled)
    split_idx = int(len(shuffled) * (1 - split_ratio))
    return shuffled[:split_idx], shuffled[split_idx:]
