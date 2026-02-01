"""
Matcher utils for entity extraction.
"""

from spacy.language import Language
from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc, Span

from meridian.core.models import MeridianLabel
from meridian.services.extraction.gazetteer.loader import load_gazetteer
from meridian.services.extraction.patterns.postcode import find_postcode_matches


def _char_range_to_span(doc: Doc, start_char: int, end_char: int) -> Span | None:
    """
    Map character range to a single token span; return None if not aligned.

    Args:
        doc: Input spaCy document.
        start_char: Start character position.
        end_char: End character position.

    Returns:
        Span with labelled spans.
    """
    start_tok = end_tok = None
    for token in doc:
        if token.idx <= start_char < token.idx + len(token.text):
            start_tok = token.i
        if token.idx < end_char <= token.idx + len(token.text):
            end_tok = token.i + 1
            break
    if start_tok is not None and end_tok is not None:
        return Span(doc, start_tok, end_tok, label=MeridianLabel.POSTCODE_AREA.value)
    return None


def build_phrase_matcher(nlp: Language) -> PhraseMatcher:
    """
    Build a PhraseMatcher with LOCAL_AUTHORITY and REGION phrases.

    Args:
        nlp: spaCy language model.

    Returns:
        PhraseMatcher with LOCAL_AUTHORITY and REGION phrases.
    """
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    gazetteer = load_gazetteer()
    la_docs = list(nlp.pipe(row.name for row in gazetteer.local_authorities))
    rgn_docs = list(nlp.pipe(row.name for row in gazetteer.regions))
    matcher.add(MeridianLabel.LOCAL_AUTHORITY.value, la_docs)
    matcher.add(MeridianLabel.REGION.value, rgn_docs)
    return matcher


def find_phrase_spans(doc: Doc, matcher: PhraseMatcher) -> list[Span]:
    """
    Run phrase matcher and return labelled spans.

    Args:
        doc: Input spaCy document.
        matcher: PhraseMatcher to use.

    Returns:
        List of spans with labelled spans.
    """
    return [
        Span(doc, match.start, match.end, label=doc.vocab.strings[match.label])
        for match in matcher(doc, as_spans=True)
    ]


def find_postcode_spans(doc: Doc) -> list[Span]:
    """
    Find UK postcode outcode spans in doc.

    Args:
        doc: Input spaCy document.

    Returns:
        List of spans with labelled spans.
    """
    return [
        span
        for start_char, end_char in find_postcode_matches(doc.text)
        if (span := _char_range_to_span(doc, start_char, end_char)) is not None
    ]


def merge_spans(spans: list[Span]) -> list[Span]:
    """
    Return non-overlapping spans, sorted by start.

    Args:
        spans: List of input spans.

    Returns:
        List of non-overlapping spans, sorted by start.
    """
    if not spans:
        return []
    sorted_spans = sorted(spans, key=lambda s: (s.start, -s.end))
    merged: list[Span] = [sorted_spans[0]]
    for span in sorted_spans[1:]:
        if span.start >= merged[-1].end:
            merged.append(span)
    return merged
