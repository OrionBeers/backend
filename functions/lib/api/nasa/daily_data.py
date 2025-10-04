import requests
from typing import Optional
from datetime import datetime
import logging

from .types import NASAPowerResponse

# NASA Power API Configuration
NASA_POWER_BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

DEFAULT_PARAMETERS = "T2M,RH2M,PRECTOTCORR,GWETROOT,GWETTOP,PRECSNO,TSOIL5"


def _validate_coordinates(latitude: float, longitude: float) -> None:
    """Validate latitude and longitude values."""
    if not (-90 <= latitude <= 90):
        raise ValueError(f"Latitude must be between -90 and 90, got {latitude}")
    if not (-180 <= longitude <= 180):
        raise ValueError(f"Longitude must be between -180 and 180, got {longitude}")


def _validate_dates(start_date: str, end_date: str) -> None:
    """Validate date format and range."""
    try:
        start = datetime.strptime(start_date, "%Y%m%d")
        end = datetime.strptime(end_date, "%Y%m%d")

        if start >= end:
            raise ValueError("Start date must be before end date")

    except ValueError as e:
        if "time data" in str(e):
            raise ValueError("Dates must be in YYYYMMDD format")
        raise


def fetch_nasa_daily_data(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
) -> NASAPowerResponse:
    """
    Fetch daily meteorological data from NASA Power API.

    Args:
        latitude: Point latitude value
        longitude: Point longitude value
        start_date: Start date formatted as YYYYMMDD
        end_date: End date formatted as YYYYMMDD

    Returns:
        NASAPowerResponse object containing the structured API response data

    Raises:
        requests.RequestException: If API request fails
        ValueError: If parameters are invalid
    """
    # Validate input parameters
    _validate_coordinates(latitude, longitude)
    _validate_dates(start_date, end_date)

    # Build query parameters
    params = {
        "start": start_date,
        "end": end_date,
        "latitude": latitude,
        "longitude": longitude,
        "community": "re",
        "parameters": DEFAULT_PARAMETERS,
        "format": "json",
        "units": "metric",
        "header": "true",
    }

    try:
        logging.info(f"Fetching NASA data for coordinates ({latitude}, {longitude})")
        response = requests.get(
            NASA_POWER_BASE_URL,
            params=params,
            headers={"accept": "application/json"},
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        logging.info("Successfully fetched NASA data")
        return NASAPowerResponse.from_dict(data)

    except requests.RequestException as e:
        logging.error(f"Failed to fetch NASA data: {e}")
        raise
