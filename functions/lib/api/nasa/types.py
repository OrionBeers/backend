"""
Type definitions for NASA Power API responses.
"""

from typing import Dict, Any, List, TypedDict
from dataclasses import dataclass


class ParameterData(TypedDict, total=False):
    """
    Typed dictionary for parameter data with code completion.
    
    Each parameter maps to a dictionary of {date_string: value}.
    Date strings are in YYYYMMDD format for daily data.
    """
    T2M: Dict[str, float]  # Temperature at 2 Meters (°C)
    RH2M: Dict[str, float]  # Relative Humidity at 2 Meters (%)
    PRECTOTCORR: Dict[str, float]  # Precipitation Corrected (mm/day)
    GWETROOT: Dict[str, float]  # Root Zone Soil Wetness (1)
    GWETTOP: Dict[str, float]  # Surface Soil Wetness (1)
    PRECSNO: Dict[str, float]  # Snow Precipitation (mm/day)
    TSOIL5: Dict[str, float]  # Soil Temperatures Layer 5 (°C)


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
    parameter: ParameterData  # Typed parameter data with code completion


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
                parameter=data["properties"]["parameter"]  # type: ignore[typeddict-item]
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
