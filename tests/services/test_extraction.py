"""
Tests for entity extraction.
"""

from meridian.core.models import ExtractionResult
from meridian.services.extraction import EntityExtractor


class TestEntityExtractor:
    """
    Tests for EntityExtractor.
    """

    def test_extractor_initialises(self, extractor: EntityExtractor) -> None:
        """
        Extractor should initialise without errors.
        """
        assert extractor is not None
        assert extractor.nlp is not None

    def test_extract_returns_result(self, extractor: EntityExtractor) -> None:
        """
        Extract should return an ExtractionResult.
        """
        result = extractor.extract("Hello world")
        assert isinstance(result, ExtractionResult)
        assert result.text == "Hello world"

    def test_extract_batch_returns_list(self, extractor: EntityExtractor) -> None:
        """
        Extract batch should return a list of results.
        """
        results = extractor.extract_batch(["Text one", "Text two"])
        assert len(results) == 2
        assert all(isinstance(r, ExtractionResult) for r in results)


class TestLocalAuthorityExtraction:
    """
    Tests for LOCAL_AUTHORITY extraction.
    """

    def test_extracts_council_name(self, extractor: EntityExtractor) -> None:
        """
        Should extract 'Manchester City Council' as LOCAL_AUTHORITY.
        """
        result = extractor.extract("I need to contact Manchester City Council")
        labels = [entity.label for entity in result.entities]
        assert "LOCAL_AUTHORITY" in labels, "Should extract LOCAL_AUTHORITY"

    def test_extracts_council_short_form(self, extractor: EntityExtractor) -> None:
        """
        Should extract 'Oldham Council' as LOCAL_AUTHORITY.
        """
        result = extractor.extract("Contact Oldham Council about bins")
        labels = [entity.label for entity in result.entities]
        assert "LOCAL_AUTHORITY" in labels, "Should extract LOCAL_AUTHORITY"

    def test_extracts_authority_name_only(self, extractor: EntityExtractor) -> None:
        """
        Should extract 'Stockport' in council context as LOCAL_AUTHORITY.
        """
        result = extractor.extract("Council tax in Stockport is too high")
        labels = [entity.label for entity in result.entities]
        assert "LOCAL_AUTHORITY" in labels, "Should extract LOCAL_AUTHORITY"


class TestRegionExtraction:
    """
    Tests for REGION extraction.
    """

    def test_extracts_region_name(self, extractor: EntityExtractor) -> None:
        """
        Should extract 'North West' as REGION.
        """
        result = extractor.extract("Jobs in the North West are increasing")
        labels = [entity.label for entity in result.entities]
        assert "REGION" in labels, "Should extract REGION"

    def test_extracts_london_as_region(self, extractor: EntityExtractor) -> None:
        """
        Should extract 'London' as REGION when used regionally.
        """
        result = extractor.extract("Property prices in London are rising")
        labels = [entity.label for entity in result.entities]
        assert "REGION" in labels, "Should extract REGION"


class TestPostcodeExtraction:
    """
    Tests for POSTCODE_AREA extraction.
    """

    def test_extracts_full_postcode(self, extractor: EntityExtractor) -> None:
        """
        Should extract postcode area from full postcode.
        """
        result = extractor.extract("Delivery to M4 5AD please")
        labels = [entity.label for entity in result.entities]
        assert "POSTCODE_AREA" in labels, "Should extract POSTCODE_AREA"

    def test_extracts_postcode_area_only(self, extractor: EntityExtractor) -> None:
        """
        Should extract standalone postcode area.
        """
        result = extractor.extract("The SW1 area is expensive")
        labels = [entity.label for entity in result.entities]
        assert "POSTCODE_AREA" in labels, "Should extract POSTCODE_AREA"
