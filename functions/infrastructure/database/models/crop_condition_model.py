from datetime import datetime
from pydantic import Field
from bson.objectid import ObjectId
from infrastructure.database.interface.model_interface import ModelInterface


class CropConditionModel(ModelInterface):
    id: str = Field(alias="_id", default_factory=lambda: str(ObjectId()))
    crop_key: str
    crop_name: str
    temperature: float  # °C
    humidity: float  # %
    root_soil_moisture: float  # 0-1
    top_soil_moisture: float  # 0-1
    soil_temperature: float  # °C
    snow_precipitation: float  # mm/day
    rain_precipitation: float  # mm/day

    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
