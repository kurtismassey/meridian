"""
Entity extraction service.
"""

from functools import lru_cache

import spacy
from spacy.language import Language
from spacy.tokens import Doc

from meridian.config.logging import get_logger
from meridian.core.models import ExtractedEntity, ExtractionResult
from meridian.services.extraction.matchers import (
    build_phrase_matcher,
    find_phrase_spans,
    find_postcode_spans,
    merge_spans,
)

logger = get_logger(__name__)


class EntityExtractor:
    """
    Extract entities from text.
    """

    def __init__(self, nlp: Language | None = None) -> None:
        """
        Initialise the extractor.

        Args:
            nlp: Optional spaCy language model. If not provided,
                 loads a blank English model.
        """
        if nlp is None:
            nlp = spacy.blank("en")
        self._nlp = nlp
        self._phrase_matcher = build_phrase_matcher(nlp)

    @property
    def nlp(self) -> Language:
        """
        Return the spaCy language model.

        Returns:
            spaCy language model.
        """
        return self._nlp

    def _apply_matchers(self, doc: Doc) -> Doc:
        """
        Run matchers and set doc.ents.

        Args:
            doc: Input spaCy document.

        Returns:
            Processed spaCy document with entities.
        """
        spans = find_phrase_spans(doc, self._phrase_matcher)
        spans.extend(find_postcode_spans(doc))
        doc.ents = merge_spans(spans)
        return doc

    def extract(self, text: str) -> ExtractionResult:
        """
        Extract entities from text.

        Args:
            text: Input text to process.

        Returns:
            ExtractionResult with extracted entities.
        """
        doc = self._nlp(text)
        doc = self._apply_matchers(doc)
        entities = self._extract_from_doc(doc)
        return ExtractionResult(text=text, entities=entities)

    def _extract_from_doc(self, doc: Doc) -> list[ExtractedEntity]:
        """
        Convert doc.ents to ExtractedEntity list.

        Args:
            doc: Input spaCy document.

        Returns:
            List of extracted entities.
        """
        return [
            ExtractedEntity(
                text=entity.text,
                label=entity.label_,
                start=entity.start_char,
                end=entity.end_char,
            )
            for entity in doc.ents
        ]

    def extract_batch(self, texts: list[str]) -> list[ExtractionResult]:
        """
        Extract entities from multiple texts.

        Args:
            texts: List of input texts to process.

        Returns:
            List of ExtractionResults with extracted entities.
        """
        return [
            ExtractionResult(text=doc.text, entities=self._extract_from_doc(doc))
            for doc in (self._apply_matchers(doc) for doc in self._nlp.pipe(texts))
        ]


@lru_cache(maxsize=1)
def get_extractor() -> EntityExtractor:
    """
    Get the extractor instance.

    Returns:
        EntityExtractor instance.
    """
    return EntityExtractor()
