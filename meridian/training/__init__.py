"""
Meridian NER model training.
"""

from meridian.training.evaluator import evaluate
from meridian.training.trainer import train

__all__: list[str] = ["train", "evaluate"]
