"""
NER model training.
"""

import random
from pathlib import Path
from typing import cast

import spacy
from spacy.language import Language
from spacy.pipeline import EntityRecognizer
from spacy.training import Example
from spacy.util import compounding, minibatch

from meridian.config.logging import get_logger
from meridian.config.settings import settings
from meridian.training.loader import load_data, load_default_data, split_data
from meridian.training.models import TrainingItem

logger = get_logger(__name__)


def _setup_nlp(lang: str) -> Language:
    """
    Create blank spaCy model with NER pipe.
    """
    nlp = spacy.blank(lang)
    nlp.add_pipe("ner", last=True)
    return nlp


def _add_labels(nlp: Language, data: list[TrainingItem]) -> None:
    """
    Add entity labels from training data to NER pipe.
    """
    ner = cast(EntityRecognizer, nlp.get_pipe("ner"))
    labels = {entity.label for item in data for entity in item.entities}
    for label in labels:
        ner.add_label(label)


def _create_examples(nlp: Language, data: list[TrainingItem]) -> list[Example]:
    """
    Convert TrainingItems to spaCy Examples.
    """
    examples = []
    for item in data:
        doc = nlp.make_doc(item.text)
        annotations = {
            "entities": [(e.start, e.end, e.label) for e in item.entities],
        }
        examples.append(Example.from_dict(doc, annotations))
    return examples


def _run_training(
    nlp: Language,
    examples: list[Example],
    n_iter: int,
    batch_size: int,
    dropout: float,
) -> None:
    """
    Run the training loop.
    """
    optimiser = nlp.begin_training()
    other_pipes = [p for p in nlp.pipe_names if p != "ner"]

    with nlp.disable_pipes(*other_pipes):
        sizes = compounding(1.0, float(batch_size), 1.001)

        for itn in range(n_iter):
            random.shuffle(examples)
            batches = minibatch(examples, size=sizes)
            losses: dict[str, float] = {}

            for batch in batches:
                nlp.update(batch, drop=dropout, sgd=optimiser, losses=losses)

            logger.info("Iteration %s: Losses %s", itn + 1, losses)


def _save_model(nlp: Language, output_path: Path) -> None:
    """
    Save model to disk.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    nlp.to_disk(output_path)
    try:
        log_path = output_path.relative_to(Path.cwd())
    except ValueError:
        log_path = output_path
    logger.info("Model saved to %s", log_path)


def train(
    data_path: Path | None = None,
    output_dir: Path | None = None,
    *,
    n_iter: int | None = None,
    batch_size: int | None = None,
    dropout: float | None = None,
    lang: str | None = None,
    model_name: str | None = None,
    validation_split: float | None = None,
) -> Path:
    """
    Train the Meridian NER model.

    Args:
        data_path: Path to JSON training data. Defaults to package default.
        output_dir: Directory to save trained model. Defaults to settings.MODELS_DIR.
        n_iter: Training iterations. Defaults to settings.TRAINING_N_ITER.
        batch_size: Batch size. Defaults to settings.TRAINING_BATCH_SIZE.
        dropout: Dropout rate. Defaults to settings.TRAINING_DROPOUT.
        lang: Language code. Defaults to settings.TRAINING_LANG.
        model_name: Name for saved model. Defaults to settings.TRAINING_MODEL_NAME.
        validation_split: Fraction of data for validation. Defaults to settings.

    Returns:
        Path to the saved model directory.
    """
    items = load_data(data_path) if data_path else load_default_data()
    validation_split = validation_split or settings.TRAINING_VALIDATION_SPLIT
    train_items, _ = split_data(items, split_ratio=validation_split)

    output_dir = output_dir or settings.MODELS_DIR
    n_iter = n_iter or settings.TRAINING_N_ITER
    batch_size = batch_size or settings.TRAINING_BATCH_SIZE
    dropout = dropout or settings.TRAINING_DROPOUT
    lang = lang or settings.TRAINING_LANG
    model_name = model_name or settings.TRAINING_MODEL_NAME

    logger.info("Starting training for %s iterations...", n_iter)

    nlp = _setup_nlp(lang)
    _add_labels(nlp, train_items)
    examples = _create_examples(nlp, train_items)
    _run_training(nlp, examples, n_iter, batch_size, dropout)

    output_path = output_dir / model_name
    _save_model(nlp, output_path)
    return output_path
