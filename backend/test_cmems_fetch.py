"""
Tests for CMEMS integration.

Following TDD principles: Test FIRST, implementation second.
These tests verify the CMEMS API integration returns proper ocean condition data.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from cmems_fetch import fetch_cmems_marine_data, fetch_cmems_with_fallback
from dotenv import load_dotenv

load_dotenv()


class TestCMEMSIntegration:
    """Test suite for real CMEMS API integration"""

    def test_fetch_cmems_returns_required_fields(self):
        """
        Real CMEMS data should include temperature, oxygen, salinity, pH.
        
        Given valid coordinates
        When we fetch CMEMS data
        Then we should get ocean conditions with required fields
        """
        result = fetch_cmems_marine_data(lat=12.0, lon=80.0)
        
        # Verify required fields exist
        assert "temperature_celsius" in result, "Missing temperature"
        assert "oxygen_mol_m3" in result, "Missing oxygen"
        assert "salinity_psu" in result, "Missing salinity"
        assert "ph" in result or "ph_value" in result, "Missing pH"
        assert "coordinates" in result, "Missing coordinates"
        assert "timestamp" in result, "Missing timestamp"
        assert result["coordinates"]["latitude"] == 12.0
        assert result["coordinates"]["longitude"] == 80.0

    def test_fetch_cmems_returns_realistic_values(self):
        """
        CMEMS data should return oceanographically realistic values.
        
        Temperature: -2 to 40°C
        Salinity: 5-41 PSU
        pH: 7.5-8.3
        Oxygen: 0-400 mol/m³
        """
        result = fetch_cmems_marine_data(lat=20.0, lon=0.0)
        
        # Temperature bounds
        temp = result.get("temperature_celsius")
        assert -2 <= temp <= 40, f"Temperature {temp} out of realistic range"
        
        # Salinity bounds
        salinity = result.get("salinity_psu")
        assert 5 <= salinity <= 41, f"Salinity {salinity} out of realistic range"
        
        # pH bounds
        ph = result.get("ph", result.get("ph_value"))
        assert 7.5 <= ph <= 8.3, f"pH {ph} out of realistic range"
        
        # Oxygen bounds (mol/m³)
        oxygen = result.get("oxygen_mol_m3")
        assert 0 <= oxygen <= 400, f"Oxygen {oxygen} out of realistic range"

    def test_fetch_cmems_different_coordinates(self):
        """
        CMEMS should return different values for different locations.
        
        Equatorial waters, subtropical, and polar waters have different characteristics.
        """
        equatorial = fetch_cmems_marine_data(lat=0.0, lon=0.0)
        subtropical = fetch_cmems_marine_data(lat=30.0, lon=0.0)
        polar = fetch_cmems_marine_data(lat=-60.0, lon=0.0)
        
        # At minimum, they should return data (not fail)
        assert equatorial.get("salinity_psu") is not None
        assert subtropical.get("salinity_psu") is not None
        assert polar.get("salinity_psu") is not None
        
        # Polar regions typically cooler
        assert polar.get("temperature_celsius", 0) < subtropical.get("temperature_celsius", 20)

    def test_fetch_cmems_with_invalid_coordinates_returns_error(self):
        """
        Invalid coordinates should return error, not crash.
        """
        with pytest.raises(ValueError):
            fetch_cmems_marine_data(lat=91.0, lon=180.0)  # Invalid latitude
        
        with pytest.raises(ValueError):
            fetch_cmems_marine_data(lat=0.0, lon=181.0)  # Invalid longitude

    def test_fetch_cmems_requires_credentials(self):
        """
        CMEMS API requires valid credentials to fetch real data.
        """
        username = os.getenv("CMEMS_USERNAME")
        password = os.getenv("CMEMS_PASSWORD")
        
        assert username, "CMEMS_USERNAME not set in .env"
        assert password, "CMEMS_PASSWORD not set in .env"
        assert username != "", "CMEMS_USERNAME is empty"
        assert password != "", "CMEMS_PASSWORD is empty"

    def test_fetch_cmems_with_fallback_succeeds(self):
        """
        fetch_cmems_with_fallback should return data (real or simulated).
        
        If CMEMS API fails, should gracefully fall back to simulation.
        """
        result = fetch_cmems_with_fallback(lat=15.0, lon=45.0)
        
        # Should always return data
        assert result is not None
        assert "temperature_celsius" in result
        assert "salinity_psu" in result
        assert result["coordinates"]["latitude"] == 15.0
        assert result["coordinates"]["longitude"] == 45.0

    def test_fetch_cmems_response_format(self):
        """
        Response should follow consistent format for API integration.
        """
        result = fetch_cmems_marine_data(lat=10.0, lon=50.0)
        
        # Verify response structure
        assert isinstance(result, dict), "Response should be dict"
        assert isinstance(result.get("coordinates"), dict), "Coordinates should be dict"
        assert isinstance(result.get("timestamp"), str), "Timestamp should be string"
        
        # Numeric values should be floats or ints
        assert isinstance(result.get("temperature_celsius"), (int, float))
        assert isinstance(result.get("salinity_psu"), (int, float))


class TestCMEMSErrorHandling:
    """Test suite for CMEMS error handling and resilience"""

    def test_fetch_cmems_handles_api_timeout(self):
        """
        Should handle timeout gracefully.
        """
        with patch('cmems_fetch.copernicusmarine.subset') as mock_api:
            mock_api.side_effect = TimeoutError("API timeout")
            result = fetch_cmems_with_fallback(lat=10.0, lon=50.0)
            
            # Should fall back to simulation
            assert result is not None
            assert "temperature_celsius" in result

    def test_fetch_cmems_handles_invalid_credentials(self):
        """
        Should handle invalid credentials gracefully.
        """
        with patch.dict(os.environ, {"CMEMS_USERNAME": "invalid", "CMEMS_PASSWORD": "invalid"}):
            result = fetch_cmems_with_fallback(lat=10.0, lon=50.0)
            
            # Should fall back to simulation
            assert result is not None
            assert "temperature_celsius" in result

    def test_fetch_cmems_handles_network_error(self):
        """
        Should handle network errors gracefully.
        """
        with patch('cmems_fetch.copernicusmarine.subset') as mock_api:
            mock_api.side_effect = ConnectionError("Network error")
            result = fetch_cmems_with_fallback(lat=10.0, lon=50.0)
            
            # Should fall back to simulation
            assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
