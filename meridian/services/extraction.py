"""
Entity extraction service.
"""

from functools import lru_cache

import spacy
from spacy.language import Language
from spacy.tokens import Doc

from meridian.config.logging import get_logger
from meridian.core.models import ExtractedEntity, ExtractionResult

logger = get_logger(__name__)


class EntityExtractor:
    """
    Extract entities from text.
    """

    def __init__(self, nlp: Language | None = None) -> None:
        """
        Initialise the extractor.

        Args:
            nlp: Optional spaCy Language model. If not provided,
                 loads a blank English model.
        """
        if nlp is None:
            nlp = spacy.blank("en")
        self._nlp = nlp
        self._setup_matchers()

    def _setup_matchers(self) -> None:
        """
        Set up entity matchers.
        """
        # TODO: Add PhraseMatcher for LOCAL_AUTHORITY
        # TODO: Add PhraseMatcher for REGION
        # TODO: Add Matcher patterns for POSTCODE_AREA

    @property
    def nlp(self) -> Language:
        """
        Return the spaCy language model.
        """
        return self._nlp

    def extract(self, text: str) -> ExtractionResult:
        """
        Extract entities from text.

        Args:
            text: Input text to process.

        Returns:
            ExtractionResult with extracted entities.
        """
        doc = self._nlp(text)
        entities = self._extract_from_doc(doc)

        return ExtractionResult(
            text=text,
            entities=entities,
        )

    def _extract_from_doc(self, doc: Doc) -> list[ExtractedEntity]:
        """
        Extract entities from a processed spaCy Doc.

        Args:
            doc: Processed spaCy document.

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
            texts: List of input texts.

        Returns:
            List of extraction results.
        """
        results = []
        for doc in self._nlp.pipe(texts):
            entities = self._extract_from_doc(doc)
            results.append(
                ExtractionResult(
                    text=doc.text,
                    entities=entities,
                )
            )
        return results


@lru_cache(maxsize=1)
def get_extractor() -> EntityExtractor:
    """
    Get the extractor instance.
    """
    return EntityExtractor()
