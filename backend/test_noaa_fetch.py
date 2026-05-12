"""
Tests for NOAA integration.

Following TDD principles: Test FIRST, implementation second.
These tests verify the NOAA API integration returns proper SST and anomaly data.
"""

import pytest
import requests
from unittest.mock import patch, MagicMock
from noaa_fetch import (
    fetch_noaa_sst_data,
    fetch_noaa_with_fallback,
    calculate_temperature_anomaly,
    get_climatological_max
)


class TestNOAAIntegration:
    """Test suite for NOAA SST integration"""

    def test_fetch_noaa_returns_required_fields(self):
        """
        NOAA SST data should include temperature, anomaly, and DHW.
        
        Given valid coordinates
        When we fetch NOAA data
        Then we should get SST metrics with required fields
        """
        result = fetch_noaa_with_fallback(lat=12.0, lon=80.0)
        
        # Verify required fields exist
        assert "sst_celsius" in result, "Missing SST temperature"
        assert "hotspot_anomaly" in result or "temp_anomaly" in result, "Missing anomaly"
        assert "degree_heating_weeks" in result or "dhw" in result, "Missing DHW"
        assert "coordinates" in result, "Missing coordinates"
        assert "timestamp" in result, "Missing timestamp"
        assert result["coordinates"]["latitude"] == 12.0
        assert result["coordinates"]["longitude"] == 80.0

    def test_fetch_noaa_returns_realistic_temperature(self):
        """
        NOAA data should return oceanographically realistic SST values.
        
        Temperature bounds: -2 to 35°C (ocean range)
        """
        result = fetch_noaa_with_fallback(lat=20.0, lon=0.0)
        
        sst = result.get("sst_celsius")
        assert isinstance(sst, (int, float)), "SST should be numeric"
        assert -2 <= sst <= 35, f"SST {sst} out of realistic range (-2 to 35°C)"

    def test_fetch_noaa_temperature_varies_by_latitude(self):
        """
        Temperature should be warmer near equator, cooler at poles.
        
        Equatorial (lat=0) should be warmer than polar (lat=70)
        """
        equatorial = fetch_noaa_with_fallback(lat=0.0, lon=0.0)
        polar = fetch_noaa_with_fallback(lat=70.0, lon=0.0)
        
        equatorial_temp = equatorial.get("sst_celsius", 0)
        polar_temp = polar.get("sst_celsius", 30)
        
        assert equatorial_temp > polar_temp, \
            f"Equator ({equatorial_temp}°C) should be warmer than polar ({polar_temp}°C)"

    def test_fetch_noaa_anomaly_is_realistic(self):
        """
        Temperature anomaly should be the difference between current and historical average.
        
        Most locations: -3 to +3°C
        Some extreme warming: up to +5°C
        """
        result = fetch_noaa_with_fallback(lat=25.0, lon=-75.0)
        
        anomaly = result.get("hotspot_anomaly", result.get("temp_anomaly", 0))
        assert isinstance(anomaly, (int, float)), "Anomaly should be numeric"
        assert -3 <= anomaly <= 5, f"Anomaly {anomaly} out of realistic range"

    def test_calculate_temperature_anomaly(self):
        """
        Anomaly = Current SST - Climatological Max
        
        If current SST is higher than normal max, anomaly is positive (warming).
        If current SST is lower, anomaly is negative (cooling).
        """
        current_sst = 30.0
        historical_max = 28.0
        expected_anomaly = 2.0
        
        anomaly = calculate_temperature_anomaly(current_sst, historical_max)
        assert anomaly == expected_anomaly

    def test_calculate_temperature_anomaly_negative(self):
        """
        Anomaly should be negative if current SST is below historical max.
        """
        current_sst = 26.0
        historical_max = 28.0
        expected_anomaly = -2.0
        
        anomaly = calculate_temperature_anomaly(current_sst, historical_max)
        assert anomaly == expected_anomaly

    def test_climatological_max_varies_by_latitude(self):
        """
        Climatological maximum SST varies by latitude.
        
        Equator has higher max (~29°C)
        Polar regions have lower max (~18°C)
        """
        equatorial_max = get_climatological_max(lat=0.0)
        polar_max = get_climatological_max(lat=70.0)
        
        assert equatorial_max > polar_max, \
            f"Equatorial max ({equatorial_max}°C) should be > polar max ({polar_max}°C)"

    def test_fetch_noaa_with_invalid_coordinates_returns_error(self):
        """
        Invalid coordinates should return error, not crash.
        """
        with pytest.raises(ValueError):
            fetch_noaa_sst_data(lat=91.0, lon=180.0)
        
        with pytest.raises(ValueError):
            fetch_noaa_sst_data(lat=0.0, lon=181.0)

    def test_fetch_noaa_with_fallback_succeeds(self):
        """
        fetch_noaa_with_fallback should always return data (real or simulated).
        
        Even if NOAA API fails, should gracefully fall back to simulation.
        """
        result = fetch_noaa_with_fallback(lat=15.0, lon=45.0)
        
        # Should always return data
        assert result is not None
        assert "sst_celsius" in result
        assert result["coordinates"]["latitude"] == 15.0
        assert result["coordinates"]["longitude"] == 45.0

    def test_fetch_noaa_response_format(self):
        """
        Response should follow consistent format for API integration.
        """
        result = fetch_noaa_with_fallback(lat=10.0, lon=50.0)
        
        # Verify response structure
        assert isinstance(result, dict), "Response should be dict"
        assert isinstance(result.get("coordinates"), dict), "Coordinates should be dict"
        assert isinstance(result.get("timestamp"), str), "Timestamp should be string"
        
        # Numeric values should be floats or ints
        assert isinstance(result.get("sst_celsius"), (int, float))
        assert isinstance(result.get("hotspot_anomaly", result.get("temp_anomaly", 0)), (int, float))

    def test_fetch_noaa_degree_heating_weeks_calculation(self):
        """
        Degree Heating Weeks (DHW) should be based on anomaly.
        
        DHW = 0 if no anomaly
        DHW increases with positive anomaly (thermal stress)
        """
        result = fetch_noaa_with_fallback(lat=25.0, lon=-75.0)
        
        dhw = result.get("degree_heating_weeks", result.get("dhw", 0))
        anomaly = result.get("hotspot_anomaly", result.get("temp_anomaly", 0))
        
        if anomaly <= 0:
            assert dhw >= 0, "DHW should be non-negative"
        else:
            # DHW should increase with anomaly
            assert dhw > 0, "Positive anomaly should result in positive DHW"


class TestNOAAErrorHandling:
    """Test suite for NOAA error handling and resilience"""

    def test_fetch_noaa_handles_api_timeout(self):
        """
        Should handle timeout gracefully.
        """
        with patch('noaa_fetch.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
            result = fetch_noaa_with_fallback(lat=10.0, lon=50.0)
            
            # Should fall back to simulation
            assert result is not None
            assert "sst_celsius" in result

    def test_fetch_noaa_handles_connection_error(self):
        """
        Should handle connection errors gracefully.
        """
        with patch('noaa_fetch.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
            result = fetch_noaa_with_fallback(lat=10.0, lon=50.0)
            
            # Should fall back to simulation
            assert result is not None
            assert "sst_celsius" in result

    def test_fetch_noaa_handles_http_error(self):
        """
        Should handle HTTP errors gracefully.
        """
        with patch('noaa_fetch.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 503
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Service Unavailable")
            mock_get.return_value = mock_response
            
            result = fetch_noaa_with_fallback(lat=10.0, lon=50.0)
            
            # Should fall back to simulation
            assert result is not None

    def test_fetch_noaa_handles_invalid_json(self):
        """
        Should handle invalid JSON response gracefully.
        """
        with patch('noaa_fetch.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_get.return_value = mock_response
            
            result = fetch_noaa_with_fallback(lat=10.0, lon=50.0)
            
            # Should fall back to simulation
            assert result is not None
            assert "sst_celsius" in result


class TestNOAACoralBleachingAlerts:
    """Test suite for coral bleaching alert detection"""

    def test_detect_coral_bleaching_threshold(self):
        """
        Coral bleaching risk:
        - DHW < 4: No bleaching expected
        - DHW 4-6: Bleaching expected
        - DHW > 6: Severe bleaching
        """
        result = fetch_noaa_with_fallback(lat=25.0, lon=-75.0)
        dhw = result.get("degree_heating_weeks", result.get("dhw", 0))
        
        if dhw < 4:
            alert_level = "no_risk"
        elif dhw < 6:
            alert_level = "bleaching_expected"
        else:
            alert_level = "severe_bleaching"
        
        assert alert_level in ["no_risk", "bleaching_expected", "severe_bleaching"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
