
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from dataclasses import dataclass

# NASA Power API Configuration
NASA_POWER_BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

# Default parameters for agricultural/renewable energy community
DEFAULT_PARAMETERS = "T2M,RH2M,PRECTOTCORR,GWETROOT,GWETTOP,PRECSNO,TSOIL5"  # Ground wetness, temperature, humidity, precipitation
# | ID          | description                   |
# | ----------- | ----------------------------- |
# | T2M         | Temperature at 2 Meters       |
# | RH2M        | Relative Humidity at 2 Meters |
# | PRECTOTCORR | Precipitation Corrected       |
# | GWETROOT    | Root Zone Soil Wetness        |
# | GWETTOP     | Surface Soil Wetness          |
# | PRECSNO     | Snow Precipitation            |
# | TSOIL5      | Soil Temperatures Layer       |

@dataclass
class Geometry:
    """Geometry information for the API response."""
    type: str  # "Point"
    coordinates: List[float]  # [longitude, latitude, elevation]

@dataclass
class ParameterInfo:
    """Parameter information with units and description."""
    units: str
    longname: str

@dataclass
class ApiInfo:
    """API information."""
    version: str
    name: str

@dataclass
class Header:
    """Header information for the API response."""
    title: str
    api: ApiInfo
    sources: List[str]
    fill_value: int
    time_standard: str
    start: str
    end: str

@dataclass
class Times:
    """Timing information for the API response."""
    data: float
    process: float

@dataclass
class Properties:
    """Properties containing the parameter data."""
    parameter: Dict[str, Dict[str, float]]  # parameter_name -> {date: value}

@dataclass
class NASAPowerResponse:
    """Complete NASA Power API response structure."""
    type: str  # "Feature"
    geometry: Geometry
    properties: Properties
    header: Header
    messages: List[Any]
    parameters: Dict[str, ParameterInfo]
    times: Times

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NASAPowerResponse':
        """Create NASAPowerResponse from API response dictionary."""
        return cls(
            type=data["type"],
            geometry=Geometry(
                type=data["geometry"]["type"],
                coordinates=data["geometry"]["coordinates"]
            ),
            properties=Properties(
                parameter=data["properties"]["parameter"]
            ),
            header=Header(
                title=data["header"]["title"],
                api=ApiInfo(
                    version=data["header"]["api"]["version"],
                    name=data["header"]["api"]["name"]
                ),
                sources=data["header"]["sources"],
                fill_value=data["header"]["fill_value"],
                time_standard=data["header"]["time_standard"],
                start=data["header"]["start"],
                end=data["header"]["end"]
            ),
            messages=data["messages"],
            parameters={
                param: ParameterInfo(
                    units=info["units"],
                    longname=info["longname"]
                ) for param, info in data["parameters"].items()
            },
            times=Times(
                data=data["times"]["data"],
                process=data["times"]["process"]
            )
        )

class NASADataFetcher:
    """NASA Power API data fetcher for daily meteorological data."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize NASA data fetcher.
        
        Args:
            api_key: API key for NASA Power API (currently not required)
        """
        self.api_key = api_key
        self.base_url = NASA_POWER_BASE_URL
        
    def fetch_daily_data(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        parameters: str = DEFAULT_PARAMETERS,
        community: str = "re",
        units: str = "metric",
        format_type: str = "json"
    ) -> NASAPowerResponse:
        """
        Fetch daily meteorological data from NASA Power API.
        
        Args:
            latitude: Point latitude value
            longitude: Point longitude value
            start_date: Start date formatted as YYYYMMDD
            end_date: End date formatted as YYYYMMDD
            parameters: Comma delimited list of parameter abbreviations
            community: User community (re=renewable energy, ag=agriculture, sb=sustainable buildings)
            units: Type of units (metric or imperial)
            format_type: Response format (json)
            
    Returns:
        NASAPowerResponse object containing the structured API response data        Raises:
            requests.RequestException: If API request fails
            ValueError: If parameters are invalid
        """
        # Validate input parameters
        self._validate_coordinates(latitude, longitude)
        self._validate_dates(start_date, end_date)
        
        # Build query parameters
        params = {
            "start": start_date,
            "end": end_date,
            "latitude": latitude,
            "longitude": longitude,
            "community": community,
            "parameters": parameters,
            "format": format_type,
            "units": units,
            "header": "true"
        }
        
        try:
            logging.info(f"Fetching NASA data for coordinates ({latitude}, {longitude})")
            response = requests.get(
                self.base_url,
                params=params,
                headers={"accept": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            logging.info("Successfully fetched NASA data")
            return NASAPowerResponse.from_dict(data)
            
        except requests.RequestException as e:
            logging.error(f"Failed to fetch NASA data: {e}")
            raise
            
    def _validate_coordinates(self, latitude: float, longitude: float) -> None:
        """Validate latitude and longitude values."""
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Latitude must be between -90 and 90, got {latitude}")
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Longitude must be between -180 and 180, got {longitude}")
            
    def _validate_dates(self, start_date: str, end_date: str) -> None:
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

# Convenience function for easy usage
def fetch_nasa_daily_data(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    parameters: str = DEFAULT_PARAMETERS
) -> NASAPowerResponse:
    """
    Convenience function to fetch NASA daily data.
    
    Args:
        latitude: Point latitude value
        longitude: Point longitude value
        start_date: Start date formatted as YYYYMMDD
        end_date: End date formatted as YYYYMMDD
        parameters: Comma delimited list of parameter abbreviations
        
    Returns:
        NASAPowerResponse object containing the structured API response data
    """
    fetcher = NASADataFetcher()
    return fetcher.fetch_daily_data(
        latitude=latitude,
        longitude=longitude,
        start_date=start_date,
        end_date=end_date,
        parameters=parameters
    )

# Example usage:
# data = fetch_nasa_daily_data(
#     latitude=49.05,
#     longitude=-122.30,
#     start_date="20230101",
#     end_date="20231201"
# )
