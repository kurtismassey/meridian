"""
Meridian.
"""

import spacy
from spacy.language import Language

from meridian.core.models import RecogniseResult
from meridian.services.extraction.matchers import build_phrase_matcher
from meridian.services.extraction.service import recognise, recognise_batch


class Meridian:
    """
    UK location NER (local authority, region, postcode).

    Usage:
        meridian = Meridian()
        result = meridian.recognise("Contact Manchester City Council")
        for entity in result.entities:
            print(entity.label, entity.text)
    """

    def __init__(self, nlp: Language | None = None) -> None:
        """
        Initialise Meridian.

        Args:
            nlp: Optional spaCy language model. If not provided,
                 uses a blank English model.
        """
        self._nlp = nlp if nlp is not None else spacy.blank("en")
        self._phrase_matcher = build_phrase_matcher(self._nlp)

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
