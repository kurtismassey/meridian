"""
Dataset sources: ONS Postcode Directory and OS Open Names.

Downloads to data dir, unpacks zips and removes them.
"""

import zipfile
from pathlib import Path

import httpx
import pandas as pd

from meridian.config.logging import get_logger
from meridian.config.settings import settings
from meridian.services.extraction.gazetteer.prepare import prepare_gazetteer

logger = get_logger(__name__)


def _extract_and_prepare_onspd(zip_path: Path, extract_to: Path) -> None:
    """
    Extract ONSPD zip to extract_to, run prepare_gazetteer, delete zip.
    """
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_to)
    zip_path.unlink()
    prepare_gazetteer(extract_to)


def _has_gazetteer() -> bool:
    """
    True if local_authorities.csv and regions.csv exist.
    """
    lad = settings.DATA_DIR / "local_authorities.csv"
    rgn = settings.DATA_DIR / "regions.csv"
    return lad.exists() and rgn.exists()


def _fetch_onspd_zip(client: httpx.Client) -> bytes:
    """
    GET ONSPD URL; ArcGIS returns the zip directly (application/zip).
    """
    response = client.get(settings.ONSPD_URL, timeout=settings.HTTP_TIMEOUT)
    response.raise_for_status()
    content: bytes = response.content
    return content


def fetch_onspd(force: bool = False) -> Path:
    """
    Download ONS Postcode Directory to data dir, unpack zip, delete zip.

    Extracts into settings.DATA_DIR/onspd_extract/; returns DATA_DIR. Skips
    download if gazetteer CSVs already present and force is False.
    """
    if _has_gazetteer() and not force:
        return settings.DATA_DIR

    zip_path = settings.DATA_DIR / "onspd.zip"
    extract_to = settings.DATA_DIR / settings.ONSPD_EXTRACT_DIR

    if not zip_path.exists():
        with httpx.Client(follow_redirects=True) as client:
            zip_path.write_bytes(_fetch_onspd_zip(client))

    _extract_and_prepare_onspd(zip_path, extract_to)
    return settings.DATA_DIR


def _build_open_names_csv(zip_path: Path, dest: Path) -> None:
    """
    From open_names zip: read header, concat Data/*.csv with headers, write dest.
    """
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        header_file = next((n for n in names if "Header" in n), None)
        data_files = sorted(
            n for n in names if n.startswith("Data/") and n.endswith(".csv")
        )

        cols: list[str] | None = None
        if header_file:
            with zf.open(header_file) as f:
                cols = list(pd.read_csv(f, nrows=0).columns)

        frames: list[pd.DataFrame] = []
        for fname in data_files:
            with zf.open(fname) as f:
                df = pd.read_csv(f, header=None, dtype=str, on_bad_lines="skip")
                if cols and len(df.columns) == len(cols):
                    df.columns = cols
                frames.append(df)

    if frames:
        full = pd.concat(frames, ignore_index=True)
        full.to_csv(dest, index=False)


def fetch_open_names(force: bool = False) -> Path:
    """
    Download OS Open Names, extract zip, produce clean CSV, delete zip.

    API returns a zip containing Data/*.csv files (no headers) and
    Doc/OS_Open_Names_Header.csv. We concat all Data CSVs with proper
    headers into a single open_names.csv.
    """
    dest = settings.DATA_DIR / "open_names.csv"
    zip_path = settings.DATA_DIR / "open_names.zip"

    if dest.exists() and not force:
        return dest

    with httpx.Client(follow_redirects=True, timeout=settings.HTTP_TIMEOUT) as client:
        response = client.get(settings.OPEN_NAMES_CSV_URL)
        response.raise_for_status()
        zip_path.write_bytes(response.content)

    _build_open_names_csv(zip_path, dest)
    zip_path.unlink(missing_ok=True)
    return dest


def ensure_data(force: bool = False) -> None:
    """
    Ensure ONS/OS data in data dir; fetch if missing.
    """
    try:
        fetch_onspd(force=force)
        fetch_open_names(force=force)
    except (httpx.HTTPError, httpx.RequestError, OSError) as e:
        logger.debug("Fetch skipped (network or IO): %s", e)
