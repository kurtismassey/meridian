"""
Tests for gazetteer loading, preparation, and data sources.
"""

import io
import zipfile
from pathlib import Path
from unittest.mock import MagicMock

import httpx
import pandas as pd
from meridian.services.extraction.gazetteer.loader import (
    _dataframe_to_local_authorities,
    _dataframe_to_regions,
    get_local_authority_phrases,
    get_region_phrases,
    load_gazetteer,
)
from meridian.services.extraction.gazetteer.models import (
    Gazetteer,
    LocalAuthorityRow,
    RegionRow,
)
from meridian.services.extraction.gazetteer.prepare import (
    _clean_onspd_df,
    _find_first,
    _process_onspd_csv,
    _remove_dir,
    prepare_gazetteer,
)
from meridian.services.extraction.gazetteer.sources import (
    _build_open_names_csv,
    _has_gazetteer,
    ensure_data,
    fetch_onspd,
    fetch_open_names,
)


class TestHasGazetteer:
    """
    Tests for _has_gazetteer file existence check.
    """

    def test_returns_true_when_both_exist(self, mock_data_dir: Path) -> None:
        """
        Should return True when both CSVs exist.
        """
        (mock_data_dir / "local_authorities.csv").write_text("name,code\n")
        (mock_data_dir / "regions.csv").write_text("name,code\n")
        assert _has_gazetteer() is True

    def test_returns_false_when_la_missing(self, mock_data_dir: Path) -> None:
        """
        Should return False when local_authorities.csv is missing.
        """
        (mock_data_dir / "regions.csv").write_text("name,code\n")
        assert _has_gazetteer() is False

    def test_returns_false_when_regions_missing(self, mock_data_dir: Path) -> None:
        """
        Should return False when regions.csv is missing.
        """
        (mock_data_dir / "local_authorities.csv").write_text("name,code\n")
        assert _has_gazetteer() is False


class TestFetchOnspd:
    """
    Tests for fetch_onspd download logic.
    """

    def test_skips_download_when_gazetteer_exists(self, mock_data_dir: Path) -> None:
        """
        Should skip download if CSVs already exist.
        """
        (mock_data_dir / "local_authorities.csv").write_text("name,code\n")
        (mock_data_dir / "regions.csv").write_text("name,code\n")
        result = fetch_onspd(force=False)
        assert result == mock_data_dir


class TestFetchOpenNames:
    """Tests for fetch_open_names download logic."""

    def test_skips_download_when_csv_exists(self, mock_data_dir: Path) -> None:
        """
        Should skip download if open_names.csv already exists.
        """
        (mock_data_dir / "open_names.csv").write_text("col1,col2\n")
        result = fetch_open_names(force=False)
        assert result == mock_data_dir / "open_names.csv"


class TestBuildOpenNamesCsv:
    """
    Tests for _build_open_names_csv zip processing.
    """

    def test_builds_csv_from_zip(self, tmp_path: Path) -> None:
        """
        Should extract and combine CSVs from zip with header.
        """
        zip_path = tmp_path / "test.zip"
        dest = tmp_path / "output.csv"

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            zf.writestr("Doc/Header.csv", "NAME,TYPE,CODE\n")
            zf.writestr("Data/file1.csv", "London,City,E1\n")
            zf.writestr("Data/file2.csv", "Manchester,City,M1\n")
        zip_path.write_bytes(zip_buffer.getvalue())

        _build_open_names_csv(zip_path, dest)

        assert dest.exists()
        df = pd.read_csv(dest)
        assert len(df) == 2
        assert list(df.columns) == ["NAME", "TYPE", "CODE"]

    def test_handles_zip_without_header(self, tmp_path: Path) -> None:
        """
        Should handle zip without header file.
        """
        zip_path = tmp_path / "test.zip"
        dest = tmp_path / "output.csv"

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            zf.writestr("Data/file1.csv", "val1,val2,val3\n")
        zip_path.write_bytes(zip_buffer.getvalue())

        _build_open_names_csv(zip_path, dest)
        assert dest.exists()


class TestEnsureData:
    """
    Tests for ensure_data error handling.
    """

    def test_catches_http_errors(
        self, mock_data_dir: Path, mock_fetch_onspd: MagicMock
    ) -> None:
        """
        Should catch and log HTTP errors without raising.
        """
        mock_fetch_onspd.side_effect = httpx.RequestError("Network error")
        ensure_data()  # Should not raise

    def test_calls_fetch_functions(
        self, mock_fetch_onspd: MagicMock, mock_fetch_open_names: MagicMock
    ) -> None:
        """
        Should call both fetch functions.
        """
        ensure_data(force=True)
        mock_fetch_onspd.assert_called_once_with(force=True)
        mock_fetch_open_names.assert_called_once_with(force=True)


class TestDataframeConversions:
    """
    Tests for DataFrame to model conversions.
    """

    def test_dataframe_to_local_authorities(self) -> None:
        """
        Should convert DataFrame to LocalAuthorityRow tuple.
        """
        df = pd.DataFrame({"name": ["Council A", "Council B"], "code": ["A1", "B2"]})
        result = _dataframe_to_local_authorities(df)
        assert len(result) == 2
        assert all(isinstance(r, LocalAuthorityRow) for r in result)
        assert result[0].name == "Council A"
        assert result[0].code == "A1"

    def test_dataframe_to_regions(self) -> None:
        """
        Should convert DataFrame to RegionRow tuple.
        """
        df = pd.DataFrame({"name": ["Region X", "Region Y"], "code": ["X1", "Y2"]})
        result = _dataframe_to_regions(df)
        assert len(result) == 2
        assert all(isinstance(r, RegionRow) for r in result)

    def test_preserves_valid_codes(self) -> None:
        """
        Should preserve valid codes as strings.
        """
        df = pd.DataFrame({"name": ["Council A", "Council B"], "code": ["A1", "B2"]})
        result = _dataframe_to_local_authorities(df)
        assert result[0].code == "A1"
        assert result[1].code == "B2"


class TestLoadGazetteer:
    """
    Tests for load_gazetteer function.
    """

    def test_loads_gazetteer_from_csvs(
        self, mock_data_dir: Path, mock_ensure_data: MagicMock
    ) -> None:
        """
        Should load gazetteer from CSV files.
        """
        (mock_data_dir / "local_authorities.csv").write_text(
            "name,code\nTest Council,TC1\n"
        )
        (mock_data_dir / "regions.csv").write_text("name,code\nTest Region,TR1\n")
        load_gazetteer.cache_clear()

        result = load_gazetteer()

        assert isinstance(result, Gazetteer)
        assert len(result.local_authorities) == 1
        assert len(result.regions) == 1
        assert result.local_authorities[0].name == "Test Council"
        mock_ensure_data.assert_called_once()


class TestGetPhrases:
    """
    Tests for phrase getter functions.
    """

    def test_get_local_authority_phrases(
        self, mock_data_dir: Path, mock_ensure_data: MagicMock
    ) -> None:
        """
        Should return tuple of local authority names.
        """
        (mock_data_dir / "local_authorities.csv").write_text(
            "name,code\nCouncil A,A1\nCouncil B,B2\n"
        )
        (mock_data_dir / "regions.csv").write_text("name,code\nRegion X,X1\n")
        load_gazetteer.cache_clear()

        result = get_local_authority_phrases()
        assert "Council A" in result
        assert "Council B" in result

    def test_get_region_phrases(
        self, mock_data_dir: Path, mock_ensure_data: MagicMock
    ) -> None:
        """
        Should return tuple of region names.
        """
        (mock_data_dir / "local_authorities.csv").write_text(
            "name,code\nCouncil A,A1\n"
        )
        (mock_data_dir / "regions.csv").write_text(
            "name,code\nRegion X,X1\nRegion Y,Y2\n"
        )
        load_gazetteer.cache_clear()

        result = get_region_phrases()
        assert "Region X" in result
        assert "Region Y" in result


class TestFindFirst:
    """
    Tests for _find_first glob helper.
    """

    def test_finds_matching_file(self, tmp_path: Path) -> None:
        """
        Should return first matching file.
        """
        (tmp_path / "test.csv").write_text("data")
        result = _find_first(tmp_path, "*.csv")
        assert result is not None
        assert result.name == "test.csv"

    def test_returns_none_when_no_match(self, tmp_path: Path) -> None:
        """
        Should return None when no files match.
        """
        result = _find_first(tmp_path, "*.csv")
        assert result is None


class TestCleanOnspdDf:
    """
    Tests for _clean_onspd_df data cleaning.
    """

    def test_cleans_and_dedupes(self) -> None:
        """
        Should clean, dedupe, and sort DataFrame.
        """
        df = pd.DataFrame(
            {
                "LAD25NM": ["  Council A  ", "Council B", "Council A", ""],
                "LAD25CD": ["A1", "B2", "A1-dup", "X1"],
            }
        )
        result = _clean_onspd_df(df, "LAD25NM", "LAD25CD")
        assert len(result) == 2
        assert list(result["name"]) == ["Council A", "Council B"]
        assert result.iloc[0]["code"] == "A1"

    def test_handles_empty_dataframe(self) -> None:
        """
        Should handle DataFrame with no valid rows.
        """
        df = pd.DataFrame({"LAD25NM": ["", "  "], "LAD25CD": ["A1", "B2"]})
        result = _clean_onspd_df(df, "LAD25NM", "LAD25CD")
        assert len(result) == 0


class TestProcessOnspdCsv:
    """
    Tests for _process_onspd_csv file processing.
    """

    def test_processes_csv_file(self, mock_data_dir: Path) -> None:
        """
        Should find, clean, and write CSV.
        """
        docs = mock_data_dir / "Documents"
        docs.mkdir()
        (docs / "LAD_lookup.csv").write_text("LAD25NM,LAD25CD\nCouncil A,A1\n")

        _process_onspd_csv(docs, "**/LAD*.csv", "LAD25NM", "LAD25CD", "output.csv")

        output = mock_data_dir / "output.csv"
        assert output.exists()
        df = pd.read_csv(output)
        assert df.iloc[0]["name"] == "Council A"

    def test_skips_when_file_not_found(self, mock_data_dir: Path) -> None:
        """
        Should skip when no matching file found.
        """
        _process_onspd_csv(
            mock_data_dir, "**/MISSING*.csv", "col1", "col2", "output.csv"
        )
        assert not (mock_data_dir / "output.csv").exists()

    def test_skips_when_columns_missing(self, mock_data_dir: Path) -> None:
        """
        Should skip when required columns are missing.
        """
        (mock_data_dir / "test.csv").write_text("wrong_col,other_col\nval1,val2\n")

        _process_onspd_csv(mock_data_dir, "*.csv", "LAD25NM", "LAD25CD", "output.csv")

        assert not (mock_data_dir / "output.csv").exists()


class TestRemoveDir:
    """
    Tests for _remove_dir cleanup.
    """

    def test_removes_directory(self, tmp_path: Path) -> None:
        """
        Should remove directory and contents.
        """
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file.txt").write_text("content")

        _remove_dir(subdir)
        assert not subdir.exists()

    def test_handles_nonexistent_dir(self, tmp_path: Path) -> None:
        """
        Should not raise when directory doesn't exist.
        """
        _remove_dir(tmp_path / "nonexistent")


class TestPrepareGazetteer:
    """
    Tests for prepare_gazetteer orchestration.
    """

    def test_prepares_gazetteer_from_extract(self, mock_data_dir: Path) -> None:
        """
        Should process Documents/ and clean up extract dir.
        """
        extract = mock_data_dir / "extract"
        docs = extract / "Documents"
        docs.mkdir(parents=True)

        (docs / "LAD_lookup.csv").write_text("LAD25NM,LAD25CD\nCouncil A,A1\n")
        (docs / "RGN_lookup.csv").write_text("RGN25NM,RGN25CD\nRegion X,X1\n")

        prepare_gazetteer(extract)

        assert (mock_data_dir / "local_authorities.csv").exists()
        assert (mock_data_dir / "regions.csv").exists()
        assert not extract.exists()

    def test_skips_when_documents_missing(self, mock_data_dir: Path) -> None:
        """
        Should skip when Documents/ doesn't exist.
        """
        extract = mock_data_dir / "extract"
        extract.mkdir()

        prepare_gazetteer(extract)

        assert not (mock_data_dir / "local_authorities.csv").exists()
