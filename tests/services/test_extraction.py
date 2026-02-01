"""
Tests for entity extraction.
"""

from meridian.core.models import RecogniseResult

from meridian import Meridian


class TestMeridian:
    """
    Tests for Meridian.
    """

    def test_meridian_initialises(self, meridian: Meridian) -> None:
        """
        Meridian should initialise without errors.
        """
        assert meridian is not None

    def test_recognise_returns_result(self, meridian: Meridian) -> None:
        """
        Recognise should return a RecogniseResult.
        """
        result = meridian.recognise("Hello world")
        assert isinstance(result, RecogniseResult)
        assert result.text == "Hello world"

    def test_recognise_batch_returns_list(self, meridian: Meridian) -> None:
        """
        Recognise batch should return a list of results.
        """
        results = meridian.recognise_batch(["Text one", "Text two"])
        assert len(results) == 2
        assert all(isinstance(r, RecogniseResult) for r in results)


class TestLocalAuthorityExtraction:
    """
    Tests for LOCAL_AUTHORITY extraction.
    """

    def test_extracts_council_name(self, meridian: Meridian) -> None:
        """
        Should extract 'Manchester City Council' as LOCAL_AUTHORITY.
        """
        result = meridian.recognise("I need to contact Manchester City Council")
        labels = [entity.label for entity in result.entities]
        assert "LOCAL_AUTHORITY" in labels, "Should extract LOCAL_AUTHORITY"

    def test_extracts_council_short_form(self, meridian: Meridian) -> None:
        """
        Should extract 'Oldham Council' as LOCAL_AUTHORITY.
        """
        result = meridian.recognise("Contact Oldham Council about bins")
        labels = [entity.label for entity in result.entities]
        assert "LOCAL_AUTHORITY" in labels, "Should extract LOCAL_AUTHORITY"

    def test_extracts_authority_name_only(self, meridian: Meridian) -> None:
        """
        Should extract 'Stockport' in council context as LOCAL_AUTHORITY.
        """
        result = meridian.recognise("Council tax in Stockport is too high")
        labels = [entity.label for entity in result.entities]
        assert "LOCAL_AUTHORITY" in labels, "Should extract LOCAL_AUTHORITY"


class TestRegionExtraction:
    """
    Tests for REGION extraction.
    """

    def test_extracts_region_name(self, meridian: Meridian) -> None:
        """
        Should extract 'North West' as REGION.
        """
        result = meridian.recognise("Jobs in the North West are increasing")
        labels = [entity.label for entity in result.entities]
        assert "REGION" in labels, "Should extract REGION"

    def test_extracts_london_as_region(self, meridian: Meridian) -> None:
        """
        Should extract 'London' as REGION when used regionally.
        """
        result = meridian.recognise("Property prices in London are rising")
        labels = [entity.label for entity in result.entities]
        assert "REGION" in labels, "Should extract REGION"


class TestPostcodeExtraction:
    """
    Tests for POSTCODE_AREA extraction.
    """

    def test_extracts_full_postcode(self, meridian: Meridian) -> None:
        """
        Should extract postcode area from full postcode.
        """
        result = meridian.recognise("Delivery to M4 5AD please")
        labels = [entity.label for entity in result.entities]
        assert "POSTCODE_AREA" in labels, "Should extract POSTCODE_AREA"

    def test_extracts_postcode_area_only(self, meridian: Meridian) -> None:
        """
        Should extract standalone postcode area.
        """
        result = meridian.recognise("The SW1 area is expensive")
        labels = [entity.label for entity in result.entities]
        assert "POSTCODE_AREA" in labels, "Should extract POSTCODE_AREA"
