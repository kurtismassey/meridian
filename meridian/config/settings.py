"""
Meridian settings.
"""

from pathlib import Path

from pydantic_settings import BaseSettings

_PACKAGE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    """
    Meridian settings.
    """

    # Data paths
    DATA_DIR: Path = _PACKAGE_DIR / "services" / "extraction" / "data"
    TRAINING_DATA_DIR: Path = _PACKAGE_DIR / "training" / "data"
    MODELS_DIR: Path = _PACKAGE_DIR.parent / "models"
    ONSPD_EXTRACT_DIR: str = "onspd_extract"

    # HTTP
    HTTP_TIMEOUT: float = 120.0

    # Training
    TRAINING_DATA_FILE: str = "train.json"
    TRAINING_MODEL_NAME: str = "meridian-ner"
    TRAINING_N_ITER: int = 100
    TRAINING_DROPOUT: float = 0.2
    TRAINING_BATCH_SIZE: int = 16
    TRAINING_LANG: str = "en"
    TRAINING_VALIDATION_SPLIT: float = 0.2
    TRAINING_SEED: int = 42

    # ONS Postcode Directory (ONSPD) - geoportal.statistics.gov.uk
    # https://geoportal.statistics.gov.uk/datasets/3635ca7f69df4733af27caf86473ffa1/about
    ONSPD_URL: str = (
        "https://www.arcgis.com/sharing/rest/content/items/"
        "3635ca7f69df4733af27caf86473ffa1/data"
    )
    # OS Open Names CSV - osdatahub.os.uk
    # https://osdatahub.os.uk/data/downloads/open/OpenNames
    OPEN_NAMES_CSV_URL: str = (
        "https://api.os.uk/downloads/v1/products/OpenNames/downloads"
        "?area=GB&format=CSV&redirect"
    )


settings = Settings()
