"""
Prepare gazetteer data.
"""

import shutil
from pathlib import Path

import pandas as pd

from meridian.config.settings import settings


def _find_first(path: Path, pattern: str) -> Path | None:
    """
    First file under path matching glob pattern, or None.
    """
    return next(path.glob(pattern), None)


def _clean_onspd_df(df: pd.DataFrame, name_col: str, code_col: str) -> pd.DataFrame:
    """
    Select name/code columns, strip, drop empty, dedupe by name, sort.
    """
    out = df[[name_col, code_col]].copy()
    out.columns = ["name", "code"]
    out["name"] = out["name"].astype(str).str.strip()
    out["code"] = out["code"].astype(str).str.strip()
    out = out.dropna(subset=["name"])
    out = out[out["name"] != ""]
    out = out.drop_duplicates(subset=["name"], keep="first")
    return out.sort_values("name").reset_index(drop=True)


def _process_onspd_csv(
    docs_dir: Path,
    pattern: str,
    name_col: str,
    code_col: str,
    output_name: str,
) -> None:
    """
    Find CSV under docs_dir, clean to name/code, write to DATA_DIR/output_name.
    """
    path = _find_first(docs_dir, pattern)
    if path is None:
        return
    df = pd.read_csv(path, dtype=str)
    if name_col not in df.columns or code_col not in df.columns:
        return
    clean = _clean_onspd_df(df, name_col, code_col)
    clean.to_csv(settings.DATA_DIR / output_name, index=False)


def _remove_dir(path: Path) -> None:
    """
    Remove directory and contents if it exists.
    """
    if path.exists() and path.is_dir():
        shutil.rmtree(path)


# ONS column names
LAD_NAME_COL = "LAD25NM"
LAD_CODE_COL = "LAD25CD"
RGN_NAME_COL = "RGN25NM"
RGN_CODE_COL = "RGN25CD"


def prepare_gazetteer(extract_root: Path | None = None) -> None:
    """
    From extract_root/Documents/, extract LAD and RGN CSVs, clean, write
    local_authorities.csv and regions.csv; then remove extract_root.
    """
    root = (
        extract_root
        if extract_root is not None
        else settings.DATA_DIR / settings.ONSPD_EXTRACT_DIR
    )
    docs = root / "Documents"
    if not docs.exists():
        return

    _process_onspd_csv(
        docs, "**/LAD*.csv", LAD_NAME_COL, LAD_CODE_COL, "local_authorities.csv"
    )
    _process_onspd_csv(docs, "**/RGN*.csv", RGN_NAME_COL, RGN_CODE_COL, "regions.csv")
    _remove_dir(root)
