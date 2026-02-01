"""
Meridian.
"""

from pathlib import Path

import spacy
from spacy.language import Language

from meridian.core.models import RecogniseResult
from meridian.services.extraction.matchers import build_phrase_matcher
from meridian.services.extraction.service import recognise, recognise_batch
from meridian.training import evaluate as evaluate_model
from meridian.training import train as train_model
from meridian.training.models import EvaluationResult


class Meridian:
    """
    UK location NER (local authority, region, postcode).

    Usage:
        meridian = Meridian()
        result = meridian.recognise("Contact Manchester City Council")
        for entity in result.entities:
            print(entity.label, entity.text)
    """

    def __init__(
        self,
        nlp: Language | None = None,
        model_path: str | Path | None = None,
    ) -> None:
        """
        Initialise Meridian.

        Args:
            nlp: Optional spaCy language model.
            model_path: Path to a trained spaCy model to load.
                        Ignored if nlp is provided.
                        If neither is provided, uses a blank English model.
        """
        if nlp is not None:
            self._nlp = nlp
        elif model_path is not None:
            self._nlp = spacy.load(model_path)
        else:
            self._nlp = spacy.blank("en")

        self._phrase_matcher = build_phrase_matcher(self._nlp)

    @classmethod
    def train(
        cls,
        data_path: Path | None = None,
        output_dir: Path | None = None,
        *,
        n_iter: int | None = None,
        batch_size: int | None = None,
        validation_split: float | None = None,
    ) -> Path:
        """
        Train an NER model from JSON training data and save it to disk.

        Args:
            data_path: Path to JSON training data. Defaults to package default.
            output_dir: Directory to save the trained model.
            n_iter: Number of training iterations.
            batch_size: Training batch size.
            validation_split: Fraction of data for validation (0.0 to 1.0).

        Returns:
            Path to the saved model directory.
        """
        return train_model(
            data_path=data_path,
            output_dir=output_dir,
            n_iter=n_iter,
            batch_size=batch_size,
            validation_split=validation_split,
        )

    @classmethod
    def evaluate(
        cls,
        model_path: Path | None = None,
        data_path: Path | None = None,
        *,
        validation_split: float | None = None,
    ) -> EvaluationResult:
        """
        Evaluate an NER model against test data.

        Args:
            model_path: Path to trained model. Defaults to package default.
            data_path: Path to JSON test data. Defaults to package default.
            validation_split: Fraction of data for validation (0.0 to 1.0).

        Returns:
            EvaluationResult with overall and per-label metrics.
        """
        return evaluate_model(
            model_path=model_path,
            data_path=data_path,
            validation_split=validation_split,
        )

    def recognise(self, text: str) -> RecogniseResult:
        """
        Recognise location entities in text.

        Args:
            text: Input text.

        Returns:
            RecogniseResult.
        """
        return recognise(text, self._nlp, self._phrase_matcher)

    def recognise_batch(self, texts: list[str]) -> list[RecogniseResult]:
        """
        Recognise location entities in multiple texts.

        Args:
            texts: List of input texts.

        Returns:
            List of RecogniseResults.
        """
        return recognise_batch(texts, self._nlp, self._phrase_matcher)
