"""
NER model evaluation.
"""

from collections import defaultdict
from pathlib import Path

import spacy

from meridian.config.logging import get_logger
from meridian.config.settings import settings
from meridian.training.loader import load_data, load_default_data, split_data
from meridian.training.models import (
    EvaluationCounts,
    EvaluationResult,
    LabelMetrics,
    TrainingItem,
)

logger = get_logger(__name__)


def _compute_metrics(
    true_positives: int,
    false_positives: int,
    false_negatives: int,
    support: int,
) -> LabelMetrics:
    """
    Compute precision, recall and F1 from counts.
    """
    pred_total = true_positives + false_positives
    gold_total = true_positives + false_negatives

    precision = true_positives / pred_total if pred_total > 0 else 0.0
    recall = true_positives / gold_total if gold_total > 0 else 0.0
    pr_sum = precision + recall
    f1 = 2 * precision * recall / pr_sum if pr_sum > 0 else 0.0

    return LabelMetrics(precision=precision, recall=recall, f1=f1, support=support)


def _evaluate_items(
    nlp: spacy.language.Language,
    eval_items: list[TrainingItem],
) -> EvaluationCounts:
    """
    Compare predictions against gold labels.

    Returns:
        EvaluationCounts with per-label TP, FP, FN and support.
    """
    label_tp: dict[str, int] = defaultdict(int)
    label_fp: dict[str, int] = defaultdict(int)
    label_fn: dict[str, int] = defaultdict(int)
    label_support: dict[str, int] = defaultdict(int)

    texts = [item.text for item in eval_items]
    for doc, item in zip(nlp.pipe(texts), eval_items):
        gold_entities = {(e.start, e.end, e.label) for e in item.entities}
        pred_entities = {(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents}

        for _, _, label in gold_entities:
            label_support[label] += 1

        for entity in gold_entities & pred_entities:
            label_tp[entity[2]] += 1

        for entity in pred_entities - gold_entities:
            label_fp[entity[2]] += 1

        for entity in gold_entities - pred_entities:
            label_fn[entity[2]] += 1

    return EvaluationCounts(
        true_positives=dict(label_tp),
        false_positives=dict(label_fp),
        false_negatives=dict(label_fn),
        support=dict(label_support),
    )


def evaluate(
    model_path: Path | None = None,
    data_path: Path | None = None,
    *,
    validation_split: float | None = None,
) -> EvaluationResult:
    """
    Evaluate an NER model against test data.

    Args:
        model_path: Path to trained model. Defaults to settings default.
        data_path: Path to JSON test data. Defaults to package default.
        validation_split: Fraction of data for validation. Defaults to settings.

    Returns:
        EvaluationResult with overall and per-label metrics.
    """
    model_path = model_path or (settings.MODELS_DIR / settings.TRAINING_MODEL_NAME)
    nlp = spacy.load(model_path)

    items = load_data(data_path) if data_path else load_default_data()
    validation_split = validation_split or settings.TRAINING_VALIDATION_SPLIT
    _, eval_items = split_data(items, split_ratio=validation_split)

    logger.info("Evaluating model on %s examples...", len(eval_items))

    counts = _evaluate_items(nlp, eval_items)

    all_labels = set(counts.support.keys()) | set(counts.false_positives.keys())
    per_label: dict[str, LabelMetrics] = {}

    for label in sorted(all_labels):
        metrics = _compute_metrics(
            counts.true_positives.get(label, 0),
            counts.false_positives.get(label, 0),
            counts.false_negatives.get(label, 0),
            counts.support.get(label, 0),
        )
        per_label[label] = metrics
        logger.info(
            "%s: P=%.3f R=%.3f F1=%.3f (support=%d)",
            label,
            metrics.precision,
            metrics.recall,
            metrics.f1,
            metrics.support,
        )

    total_tp = sum(counts.true_positives.values())
    total_fp = sum(counts.false_positives.values())
    total_fn = sum(counts.false_negatives.values())
    total_support = sum(counts.support.values())

    overall = _compute_metrics(total_tp, total_fp, total_fn, total_support)
    logger.info(
        "Overall: P=%.3f R=%.3f F1=%.3f (support=%d)",
        overall.precision,
        overall.recall,
        overall.f1,
        overall.support,
    )

    return EvaluationResult(overall=overall, per_label=per_label)
