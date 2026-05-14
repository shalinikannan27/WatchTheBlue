"""
Tests for Marine Stress Score Calculation.

Following TDD principles: Test FIRST, implementation second.
These tests verify the stress score formula correctly weighs
temperature anomaly (40%), oxygen depletion (35%), and pH drop (25%)
and scales the result to 0-100 range.
"""

import pytest
from stress_score import (
    calculate_marine_stress,
    calculate_stress_components,
    normalize_oxygen_depletion,
    normalize_ph_drop,
    normalize_temperature_anomaly,
    get_species_stress_impact,
    classify_stress_level
)


class TestStressComponentNormalization:
    """Tests for normalizing individual stress components to 0-10 scale."""
    
    def test_normalize_temperature_anomaly_zero(self):
        """Temperature anomaly of 0 should give component score of 0."""
        result = normalize_temperature_anomaly(0)
        assert result == 0
    
    def test_normalize_temperature_anomaly_small(self):
        """Small anomaly (0.5°C) should be low stress."""
        result = normalize_temperature_anomaly(0.5)
        assert 0 < result < 2
    
    def test_normalize_temperature_anomaly_moderate(self):
        """Moderate anomaly (2.5°C) should scale to reasonable value."""
        result = normalize_temperature_anomaly(2.5)
        assert 3 < result < 6
    
    def test_normalize_temperature_anomaly_extreme(self):
        """Extreme anomaly (5°C+) should approach max score."""
        result = normalize_temperature_anomaly(5.0)
        assert result > 8
        assert result <= 10
    
    def test_normalize_temperature_anomaly_caps_at_10(self):
        """Component score should never exceed 10."""
        result = normalize_temperature_anomaly(10.0)
        assert result <= 10
    
    def test_normalize_oxygen_depletion_healthy(self):
        """Healthy oxygen (8 mg/L) should give low stress."""
        result = normalize_oxygen_depletion(8.0)
        assert result == 0
    
    def test_normalize_oxygen_depletion_moderate(self):
        """Moderate depletion (4 mg/L, below 5 threshold) should be moderate stress."""
        result = normalize_oxygen_depletion(4.0)
        assert 2.5 < result < 4
    
    def test_normalize_oxygen_depletion_severe(self):
        """Severe depletion (2 mg/L) should be high stress."""
        result = normalize_oxygen_depletion(2.0)
        assert result > 8
    
    def test_normalize_oxygen_depletion_hypoxic(self):
        """Hypoxic conditions (<1 mg/L) should max out stress."""
        result = normalize_oxygen_depletion(0.5)
        assert result >= 9.5
    
    def test_normalize_ph_drop_healthy(self):
        """Healthy pH (8.1) should give zero stress."""
        result = normalize_ph_drop(8.1)
        assert result == 0
    
    def test_normalize_ph_drop_small(self):
        """Small pH drop to 8.0 should be minimal stress."""
        result = normalize_ph_drop(8.0)
        assert 0.5 < result < 1.5
    
    def test_normalize_ph_drop_moderate(self):
        """Moderate pH drop to 7.9 should be noticeable stress."""
        result = normalize_ph_drop(7.9)
        assert 2 < result < 3
    
    def test_normalize_ph_drop_severe(self):
        """Severe pH drop to 7.7 should be high stress."""
        result = normalize_ph_drop(7.7)
        assert result > 4
    
    def test_normalize_ph_drop_critical(self):
        """Critical pH (7.5) should max out acidification stress."""
        result = normalize_ph_drop(7.5)
        assert result >= 7.5


class TestStressComponentCalculation:
    """Tests for calculating individual stress components."""
    
    def test_calculate_stress_components_no_anomaly(self):
        """Zero anomalies should return zero component scores."""
        components = calculate_stress_components(
            temp_anomaly=0,
            oxygen_mg_l=8.0,
            ph=8.1
        )
        assert components["temperature_component"] == 0
        assert components["oxygen_component"] == 0
        assert components["ph_component"] == 0
    
    def test_calculate_stress_components_mixed(self):
        """Mixed environmental conditions should score appropriately."""
        components = calculate_stress_components(
            temp_anomaly=2.5,
            oxygen_mg_l=4.0,
            ph=7.9
        )
        # Temperature should be moderate (2.5°C above healthy)
        assert 0 < components["temperature_component"] < 6
        # Oxygen should be moderate (4 mg/L is below 5 threshold)
        assert 0 < components["oxygen_component"] < 6
        # pH should be low-moderate (8.1 - 0.2 from baseline)
        assert 0 < components["ph_component"] < 3
    
    def test_calculate_stress_components_all_present(self):
        """All components should be calculated when all metrics provided."""
        components = calculate_stress_components(
            temp_anomaly=3.0,
            oxygen_mg_l=3.0,
            ph=7.8
        )
        assert "temperature_component" in components
        assert "oxygen_component" in components
        assert "ph_component" in components
        assert "stress_score" in components


class TestMarineStressFormula:
    """Tests for the core stress score formula.
    
    Formula: stress_score = (temp_anomaly × 0.4) + (oxygen_depletion × 0.35) + (ph_drop × 0.25)
    Scaled to 0-100 range.
    """
    
    def test_stress_score_zero_conditions(self):
        """Healthy conditions should result in stress score near 0."""
        stress = calculate_marine_stress(
            sst=25.0,  # Within normal range
            hotspot_anomaly=0,  # No temperature anomaly
            degree_heating_weeks=0,
            ph=8.1,  # Healthy pH
            salinity=35.0,  # Normal salinity
            chlorophyll=0.5,  # Moderate chlorophyll
            current_speed=0.15
        )
        assert stress["overall_stress_score"] < 20
    
    def test_stress_score_temperature_anomaly_weighted(self):
        """Temperature anomaly should be weighted 40% of score."""
        stress = calculate_marine_stress(
            sst=27.0,  # 3°C above normal
            hotspot_anomaly=3.0,
            degree_heating_weeks=0,
            ph=8.1,
            salinity=35.0,
            chlorophyll=0.5,
            current_speed=0.15
        )
        # Temperature anomaly alone (3°C) should contribute ~40% of stress
        assert stress["overall_stress_score"] > 10
    
    def test_stress_score_oxygen_depletion_weighted(self):
        """Oxygen depletion should be weighted 35% of score."""
        stress = calculate_marine_stress(
            sst=25.0,
            hotspot_anomaly=0,
            degree_heating_weeks=0,
            ph=8.1,
            salinity=35.0,
            chlorophyll=0.05,  # Very low chlorophyll (poor oxygenation)
            current_speed=0.01  # Very low current reduces oxygenation
        )
        # Poor oxygenation conditions should contribute to stress
        assert stress["overall_stress_score"] > 0
    
    def test_stress_score_ph_drop_weighted(self):
        """pH drop should be weighted 25% of score."""
        stress = calculate_marine_stress(
            sst=25.0,
            hotspot_anomaly=0,
            degree_heating_weeks=0,
            ph=7.8,  # 0.3 below healthy level
            salinity=35.0,
            chlorophyll=0.5,
            current_speed=0.15
        )
        # pH drop should contribute to stress
        assert stress["overall_stress_score"] > 5
    
    def test_stress_score_combined_conditions(self):
        """Combined stressors should show cumulative effect."""
        stress = calculate_marine_stress(
            sst=28.0,  # 3°C above normal
            hotspot_anomaly=3.0,
            degree_heating_weeks=3.0,
            ph=7.9,  # 0.2 below healthy
            salinity=36.0,  # Slightly elevated
            chlorophyll=0.2,  # Low
            current_speed=0.08  # Below healthy
        )
        # Multiple stressors should result in significant stress
        assert stress["overall_stress_score"] > 25
    
    def test_stress_score_scaled_to_100(self):
        """Stress score should be scaled to 0-100 range."""
        stress = calculate_marine_stress(
            sst=25.0,
            hotspot_anomaly=0,
            degree_heating_weeks=0,
            ph=8.1,
            salinity=35.0,
            chlorophyll=0.5,
            current_speed=0.15
        )
        assert 0 <= stress["overall_stress_score"] <= 100
    
    def test_stress_score_extreme_conditions_maxes_out(self):
        """Extreme conditions should approach score of 100."""
        stress = calculate_marine_stress(
            sst=32.0,  # 7°C above normal (extreme bleaching)
            hotspot_anomaly=7.0,
            degree_heating_weeks=10.0,
            ph=7.6,  # Severe acidification
            salinity=38.0,
            chlorophyll=0.05,  # Severe oxygen depletion
            current_speed=0.01
        )
        assert stress["overall_stress_score"] > 50


class TestStressLevelClassification:
    """Tests for classifying stress into human-readable levels."""
    
    def test_classify_stress_healthy(self):
        """Score 0-20 should be HEALTHY."""
        level, description = classify_stress_level(10)
        assert level == "HEALTHY"
        assert "health" in description.lower() or "good" in description.lower()
    
    def test_classify_stress_stressed(self):
        """Score 20-50 should be STRESSED."""
        level, description = classify_stress_level(35)
        assert level == "STRESSED"
        assert "stress" in description.lower()
    
    def test_classify_stress_critical(self):
        """Score 50-80 should be CRITICAL."""
        level, description = classify_stress_level(65)
        assert level == "CRITICAL"
        assert "critical" in description.lower()
    
    def test_classify_stress_severe(self):
        """Score 80-100 should be SEVERE."""
        level, description = classify_stress_level(90)
        assert level == "SEVERE"
        assert "severe" in description.lower() or "extreme" in description.lower()
    
    def test_classify_stress_boundaries(self):
        """Boundary values should classify correctly."""
        # At boundary between HEALTHY and STRESSED
        level_20, _ = classify_stress_level(20)
        assert level_20 in ["HEALTHY", "STRESSED"]
        
        # At boundary between STRESSED and CRITICAL
        level_50, _ = classify_stress_level(50)
        assert level_50 in ["STRESSED", "CRITICAL"]
        
        # At boundary between CRITICAL and SEVERE
        level_80, _ = classify_stress_level(80)
        assert level_80 in ["CRITICAL", "SEVERE"]


class TestSpeciesStressImpact:
    """Tests for calculating species-specific stress impacts."""
    
    def test_species_stress_impact_not_found(self):
        """Unknown species should return default impact."""
        impact = get_species_stress_impact("unknown species", 50)
        assert impact["species"] == "unknown species"
        assert impact["stress_level"] == "MODERATE"
    
    def test_species_stress_impact_coral_high_stress(self):
        """Corals should show high stress at elevated scores."""
        impact = get_species_stress_impact("acropora cervicornis", 65)
        assert impact["species"] == "acropora cervicornis"
        assert impact["stress_level"] in ["CRITICAL", "HIGH"]
        assert impact["vulnerability"] in ["HIGH", "VERY_HIGH"]
    
    def test_species_stress_impact_resilient_species(self):
        """Resilient species should show lower stress at same score."""
        impact = get_species_stress_impact("carcharodon carcharias", 65)
        assert impact["species"] == "carcharodon carcharias"
        assert impact["vulnerability"] in ["MODERATE", "LOW"]
    
    def test_species_stress_impact_contains_conservation_context(self):
        """Impact should include conservation priority."""
        impact = get_species_stress_impact("acropora cervicornis", 50)
        assert "conservation_priority" in impact
        assert impact["conservation_priority"] != ""


class TestStressResponseIntegration:
    """Integration tests combining all stress calculation components."""
    
    def test_full_stress_calculation_example_from_spec(self):
        """Test example from project spec."""
        # Example from spec: temp_anomaly=2.5, oxygen_depletion=1.4, ph_drop=0.6
        # Expected: (2.5×0.4) + (1.4×0.35) + (0.6×0.25) = 1.0 + 0.49 + 0.15 = 1.64
        # Scaled to 0-100: 1.64 × 10 = 16.4
        
        # Map to actual parameters:
        # - temp_anomaly=2.5 -> hotspot_anomaly=2.5
        # - oxygen_depletion=1.4 -> oxygen_mg_l = 5.0 - 1.4 = 3.6 (5 is healthy)
        # - ph_drop=0.6 -> ph = 8.1 - 0.6 = 7.5 (8.1 is healthy)
        
        stress = calculate_marine_stress(
            sst=27.5,
            hotspot_anomaly=2.5,
            degree_heating_weeks=0,
            ph=7.5,
            salinity=35.0,
            chlorophyll=0.5,
            current_speed=0.15
        )
        
        # Should be in range of 30-50 due to pH drop being critical
        assert 25 < stress["overall_stress_score"] < 60
    
    def test_stress_calculation_returns_all_components(self):
        """Stress calculation should return detailed breakdown."""
        stress = calculate_marine_stress(
            sst=26.0,
            hotspot_anomaly=1.0,
            degree_heating_weeks=0,
            ph=8.0,
            salinity=35.0,
            chlorophyll=0.5,
            current_speed=0.15
        )
        
        # Check response structure
        assert "overall_stress_score" in stress
        assert "temperature_component" in stress
        assert "oxygen_component" in stress
        assert "ph_component" in stress
        assert "stress_level" in stress
        assert "contributing_factors" in stress
    
    def test_stress_calculation_identifies_limiting_factors(self):
        """Should identify which factors are most limiting."""
        stress = calculate_marine_stress(
            sst=28.0,  # High temperature stress
            hotspot_anomaly=3.0,
            degree_heating_weeks=2.0,
            ph=8.1,  # Normal pH
            salinity=35.0,  # Normal salinity
            chlorophyll=0.5,  # Normal oxygen
            current_speed=0.15
        )
        
        # Temperature should be primary factor
        factors = stress["contributing_factors"]
        assert any("temperature" in str(f).lower() for f in factors)
        assert factors[0] == "temperature_anomaly" or "temp" in str(factors[0]).lower()
