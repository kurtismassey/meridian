"""
Training data models.
"""

from pydantic import BaseModel, Field


class EntityAnnotation(BaseModel):
    """
    Single entity span: character start, end and label.
    """

    start: int = Field(description="Start character offset")
    end: int = Field(description="End character offset")
    label: str = Field(description="Entity label (e.g. REGION, LOCAL_AUTHORITY)")


class TrainingItem(BaseModel):
    """
    One training example: text and its entity annotations.
    """

    text: str = Field(description="Raw text")
    entities: list[EntityAnnotation] = Field(
        default_factory=list,
        description="Entity spans in the text",
    )


class EvaluationCounts(BaseModel):
    """
    Per-label counts for evaluation (TP, FP, FN, support).
    """

    true_positives: dict[str, int] = Field(
        default_factory=dict,
        description="True positives per label",
    )
    false_positives: dict[str, int] = Field(
        default_factory=dict,
        description="False positives per label",
    )
    false_negatives: dict[str, int] = Field(
        default_factory=dict,
        description="False negatives per label",
    )
    support: dict[str, int] = Field(
        default_factory=dict,
        description="Gold entity count per label",
    )


class LabelMetrics(BaseModel):
    """
    Precision, recall and F1 for a single entity label.
    """

    precision: float = Field(description="Precision (0.0 to 1.0)")
    recall: float = Field(description="Recall (0.0 to 1.0)")
    f1: float = Field(description="F1 score (0.0 to 1.0)")
    support: int = Field(description="Number of gold entities for this label")


class EvaluationResult(BaseModel):
    """
    NER model evaluation results.
    """

    overall: LabelMetrics = Field(description="Aggregate metrics across all labels")
    per_label: dict[str, LabelMetrics] = Field(
        default_factory=dict,
        description="Metrics per entity label",
    )
