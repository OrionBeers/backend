#!/usr/bin/env python3
"""
Unit tests for NASA daily data API fetcher.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from functions.lib.api.nasa.daily_data import fetch_nasa_daily_data, _validate_coordinates, _validate_dates
from functions.lib.api.nasa.types import NASAPowerResponse


class TestNASADataFetcher(unittest.TestCase):
    """Test cases for NASA Power API data fetcher."""

    def test_validate_coordinates_valid(self):
        """Test coordinate validation with valid values."""
        # Should not raise any exception
        _validate_coordinates(49.05, -122.30)
        _validate_coordinates(0, 0)
        _validate_coordinates(-90, -180)
        _validate_coordinates(90, 180)

    def test_validate_coordinates_invalid_latitude(self):
        """Test coordinate validation with invalid latitude."""
        with self.assertRaises(ValueError) as context:
            _validate_coordinates(91, 0)
        self.assertIn("Latitude must be between -90 and 90", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            _validate_coordinates(-91, 0)
        self.assertIn("Latitude must be between -90 and 90", str(context.exception))

    def test_validate_coordinates_invalid_longitude(self):
        """Test coordinate validation with invalid longitude."""
        with self.assertRaises(ValueError) as context:
            _validate_coordinates(0, 181)
        self.assertIn("Longitude must be between -180 and 180", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            _validate_coordinates(0, -181)
        self.assertIn("Longitude must be between -180 and 180", str(context.exception))

    def test_validate_dates_valid(self):
        """Test date validation with valid dates."""
        # Should not raise any exception
        _validate_dates("20241001", "20241003")
        _validate_dates("20240101", "20241231")

    def test_validate_dates_invalid_format(self):
        """Test date validation with invalid format."""
        with self.assertRaises(ValueError) as context:
            _validate_dates("2024-10-01", "20241003")
        self.assertIn("Dates must be in YYYYMMDD format", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            _validate_dates("20241001", "2024-10-03")
        self.assertIn("Dates must be in YYYYMMDD format", str(context.exception))

    def test_validate_dates_invalid_range(self):
        """Test date validation with invalid date range."""
        with self.assertRaises(ValueError) as context:
            _validate_dates("20241003", "20241001")
        self.assertIn("Start date must be before end date", str(context.exception))

    @patch('functions.lib.api.nasa.daily_data.requests.get')
    def test_fetch_nasa_daily_data_success(self, mock_get):
        """Test successful API call."""
        # Mock response data
        mock_response_data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [-122.30, 49.05, 148.97]
            },
            "properties": {
                "parameter": {
                    "T2M": {"20241001": 15.2, "20241002": 16.1}
                }
            },
            "header": {
                "title": "NASA/POWER Source Native Resolution Daily Data",
                "api": {"version": "v2.8.0", "name": "POWER Daily API"},
                "sources": ["POWER", "MERRA2"],
                "fill_value": -999,
                "time_standard": "LST",
                "start": "20241001",
                "end": "20241002"
            },
            "messages": [],
            "parameters": {
                "T2M": {"units": "C", "longname": "Temperature at 2 Meters"}
            },
            "times": {"data": 0.5, "process": 0.02}
        }
        
        # Configure mock
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test the function
        result = fetch_nasa_daily_data(
            latitude=49.05,
            longitude=-122.30,
            start_date="20241001",
            end_date="20241002"
        )
        
        # Assertions
        self.assertIsInstance(result, NASAPowerResponse)
        self.assertEqual(result.type, "Feature")
        self.assertEqual(result.geometry.type, "Point")
        self.assertEqual(result.geometry.coordinates, [-122.30, 49.05, 148.97])
        self.assertIn("T2M", dict(result.properties.parameter))
        self.assertEqual(result.header.api.name, "POWER Daily API")

    @patch('functions.lib.api.nasa.daily_data.requests.get')
    def test_fetch_nasa_daily_data_api_error(self, mock_get):
        """Test API error handling."""
        # Configure mock to raise an exception
        mock_get.side_effect = Exception("API Error")
        
        # Test that the function raises the exception
        with self.assertRaises(Exception) as context:
            fetch_nasa_daily_data(
                latitude=49.05,
                longitude=-122.30,
                start_date="20241001",
                end_date="20241002"
            )
        self.assertIn("API Error", str(context.exception))

    def test_fetch_nasa_daily_data_invalid_input(self):
        """Test function with invalid input parameters."""
        # Test invalid coordinates
        with self.assertRaises(ValueError):
            fetch_nasa_daily_data(
                latitude=100,  # Invalid
                longitude=-122.30,
                start_date="20241001",
                end_date="20241002"
            )
        
        # Test invalid dates
        with self.assertRaises(ValueError):
            fetch_nasa_daily_data(
                latitude=49.05,
                longitude=-122.30,
                start_date="2024-10-01",  # Invalid format
                end_date="20241002"
            )


class TestIntegration(unittest.TestCase):
    """Integration tests that make real API calls."""
    
    @unittest.skip("Skip real API calls in unit tests - enable manually for integration testing")
    def test_real_api_call(self):
        """Test with real API call (disabled by default)."""
        result = fetch_nasa_daily_data(
            latitude=49.05,
            longitude=-122.30,
            start_date="20241001",
            end_date="20241002"
        )
        
        self.assertIsInstance(result, NASAPowerResponse)
        self.assertEqual(result.type, "Feature")
        self.assertTrue(len(dict(result.properties.parameter)) > 0)


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
