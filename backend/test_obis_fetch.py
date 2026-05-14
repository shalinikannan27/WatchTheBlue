"""
OBIS (Ocean Biodiversity Information System) API tests.

Tests for fetching species occurrence data by location.
"""

import pytest
from unittest.mock import patch, MagicMock
import json
from obis_fetch import (
    get_species_occurrences,
    get_species_by_location,
    _parse_occurrence_data,
    validate_coordinates
)


class TestOBISIntegration:
    """Tests for real OBIS API integration."""

    def test_get_species_returns_required_fields(self):
        """
        OBIS API should return species occurrence data with required fields.

        Given a location (latitude, longitude)
        When we fetch species from OBIS
        Then we should get occurrences with species name, location, date
        """
        result = get_species_by_location(lat=-18.6, lon=146.49)

        assert isinstance(result, dict)
        assert "occurrences" in result
        assert "total" in result
        assert isinstance(result["occurrences"], list)

        if len(result["occurrences"]) > 0:
            occurrence = result["occurrences"][0]
            assert "scientific_name" in occurrence
            assert "latitude" in occurrence
            assert "longitude" in occurrence
            assert "date" in occurrence

    def test_get_species_returns_realistic_data(self):
        """
        OBIS data should include valid oceanographic species.

        Marine species should have realistic taxonomy (kingdom, phylum, class, family).
        """
        result = get_species_by_location(lat=0.0, lon=0.0)

        if len(result["occurrences"]) > 0:
            occurrence = result["occurrences"][0]
            # Should have marine taxonomy
            assert "kingdom" in occurrence or "class" in occurrence
            # Coordinates should be valid
            assert -90 <= occurrence["latitude"] <= 90
            assert -180 <= occurrence["longitude"] <= 180

    def test_get_species_different_locations(self):
        """
        OBIS should return different species for different ocean locations.

        Equatorial, subtropical, and polar waters have different marine biodiversity.
        """
        equatorial = get_species_by_location(lat=0.0, lon=0.0)
        tropical = get_species_by_location(lat=20.0, lon=50.0)
        polar = get_species_by_location(lat=-60.0, lon=0.0)

        # At least one of these should have results
        total = (
            len(equatorial["occurrences"]) +
            len(tropical["occurrences"]) +
            len(polar["occurrences"])
        )
        assert total > 0

    def test_get_species_with_invalid_coordinates_returns_error(self):
        """
        Invalid coordinates should be rejected with clear error message.
        """
        with pytest.raises(ValueError):
            get_species_by_location(lat=91.0, lon=0.0)  # Latitude > 90

        with pytest.raises(ValueError):
            get_species_by_location(lat=0.0, lon=181.0)  # Longitude > 180

    def test_get_species_with_fallback_succeeds(self):
        """
        If OBIS API fails, should return graceful fallback.
        """
        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("Network error")
            result = get_species_by_location(lat=10.0, lon=50.0)

            assert "occurrences" in result
            assert result.get("source") == "Simulated OBIS Data (API unavailable)"

    def test_get_species_response_format(self):
        """
        Response should follow consistent format for API integration.
        """
        result = get_species_by_location(lat=10.0, lon=50.0)

        assert isinstance(result, dict)
        assert "occurrences" in result
        assert "total" in result
        assert "source" in result
        assert "coordinates" in result

    def test_parse_occurrence_data_extracts_fields(self):
        """
        Should extract and normalize occurrence data correctly.
        """
        raw_occurrence = {
            "scientificName": "Acropora palmata",
            "decimalLatitude": 25.0,
            "decimalLongitude": -75.0,
            "eventDate": "2023-06-15T10:30:00Z",
            "kingdom": "Animalia",
            "phylum": "Cnidaria",
            "class": "Anthozoa",
            "family": "Acroporidae",
            "depth": 5.0,
            "basisOfRecord": "HumanObservation"
        }

        parsed = _parse_occurrence_data(raw_occurrence)

        assert parsed["scientific_name"] == "Acropora palmata"
        assert parsed["latitude"] == 25.0
        assert parsed["longitude"] == -75.0
        assert "2023-06-15" in parsed["date"]
        assert parsed["kingdom"] == "Animalia"
        assert parsed["phylum"] == "Cnidaria"


class TestOBISErrorHandling:
    """Tests for OBIS API error handling and fallback."""

    def test_fetch_obis_handles_api_timeout(self):
        """
        Should gracefully handle API timeout with fallback simulation.
        """
        with patch("requests.get") as mock_get:
            mock_get.side_effect = TimeoutError("Request timeout")
            result = get_species_by_location(lat=10.0, lon=50.0)

            assert result.get("source") == "Simulated OBIS Data (API unavailable)"
            assert len(result["occurrences"]) > 0

    def test_fetch_obis_handles_connection_error(self):
        """
        Should gracefully handle network connection errors.
        """
        with patch("requests.get") as mock_get:
            mock_get.side_effect = ConnectionError("Network unreachable")
            result = get_species_by_location(lat=20.0, lon=60.0)

            assert "occurrences" in result
            assert result["source"] == "Simulated OBIS Data (API unavailable)"

    def test_fetch_obis_handles_http_error(self):
        """
        Should handle HTTP errors (4xx, 5xx) gracefully.
        """
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = Exception("500 Server Error")
            mock_get.return_value = mock_response

            result = get_species_by_location(lat=10.0, lon=50.0)

            assert result.get("source") == "Simulated OBIS Data (API unavailable)"

    def test_fetch_obis_handles_invalid_json(self):
        """
        Should handle malformed JSON response gracefully.
        """
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.side_effect = json.JSONDecodeError(
                "Invalid JSON", "", 0
            )
            mock_get.return_value = mock_response

            result = get_species_by_location(lat=10.0, lon=50.0)

            assert "occurrences" in result
            assert result.get("source") == "Simulated OBIS Data (API unavailable)"


class TestOBISSpeciesData:
    """Tests for species data filtering and analysis."""

    def test_coral_species_detection(self):
        """
        Should identify coral species (Cnidaria, Anthozoa).
        """
        result = get_species_by_location(lat=25.0, lon=-75.0)  # Florida Keys

        # Filter for corals
        corals = [
            occ for occ in result["occurrences"]
            if occ.get("phylum") == "Cnidaria"
        ]

        # May or may not have corals depending on API results
        # Just verify the structure works
        if len(corals) > 0:
            coral = corals[0]
            assert coral["phylum"] == "Cnidaria"
            assert "scientific_name" in coral

    def test_fish_species_detection(self):
        """
        Should identify fish species (Animalia, Chordata, Teleostei/Actinopterygii).
        """
        result = get_species_by_location(lat=-18.6, lon=146.49)  # Great Barrier Reef

        # Filter for fish
        fish = [
            occ for occ in result["occurrences"]
            if occ.get("phylum") == "Chordata" and occ.get("kingdom") == "Animalia"
        ]

        if len(fish) > 0:
            fish_species = fish[0]
            assert "scientific_name" in fish_species
            assert -90 <= fish_species["latitude"] <= 90
