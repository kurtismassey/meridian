"""
Entity extraction service.
"""

from spacy.language import Language
from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc

from meridian.core.models import (
    MeridianLabel,
    RecogniseEntity,
    RecogniseResult,
)
from meridian.services.extraction.matchers import (
    find_phrase_spans,
    find_postcode_spans,
    merge_spans,
)


def _apply_matchers(doc: Doc, phrase_matcher: PhraseMatcher) -> Doc:
    """
    Run phrase and postcode matchers and set doc.ents.

    Args:
        doc: Input spaCy document.
        phrase_matcher: PhraseMatcher for LOCAL_AUTHORITY and REGION.

    Returns:
        Doc with entities set.
    """
    spans = list(doc.ents)
    spans.extend(find_phrase_spans(doc, phrase_matcher))
    spans.extend(find_postcode_spans(doc))
    doc.ents = merge_spans(spans)
    return doc


def _doc_to_entities(doc: Doc) -> list[RecogniseEntity]:
    """
    Convert doc.ents to RecogniseEntity list.

    Args:
        doc: Processed spaCy document.

    Returns:
        List of recognised entities.
    """
    return [
        RecogniseEntity(
            text=entity.text,
            label=MeridianLabel(entity.label_),
            start=entity.start_char,
            end=entity.end_char,
        )
        for entity in doc.ents
    ]


def recognise(
    text: str,
    nlp: Language,
    phrase_matcher: PhraseMatcher,
) -> RecogniseResult:
    """
    Recognise location entities in text.

    Args:
        text: Input text.
        nlp: spaCy language model.
        phrase_matcher: PhraseMatcher for LOCAL_AUTHORITY and REGION.

    Returns:
        RecogniseResult with text and entities.
    """
    doc = nlp(text)
    doc = _apply_matchers(doc, phrase_matcher)
    entities = _doc_to_entities(doc)
    return RecogniseResult(text=text, entities=entities)


def recognise_batch(
    texts: list[str],
    nlp: Language,
    phrase_matcher: PhraseMatcher,
) -> list[RecogniseResult]:
    """
    Recognise location entities in multiple texts.

    Args:
        texts: List of input texts.
        nlp: spaCy language model.
        phrase_matcher: PhraseMatcher for LOCAL_AUTHORITY and REGION.

    Returns:
        List of RecogniseResults.
    """
    return [
        RecogniseResult(text=doc.text, entities=_doc_to_entities(doc))
        for doc in (_apply_matchers(doc, phrase_matcher) for doc in nlp.pipe(texts))
    ]
