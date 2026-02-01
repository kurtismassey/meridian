"""
Meridian settings.
"""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Meridian settings.
    """

    DATA_DIR: Path = Path(__file__).parent.parent / "services" / "extraction" / "data"
    ONSPD_EXTRACT_DIR: str = "onspd_extract"

    HTTP_TIMEOUT: float = 120.0

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
