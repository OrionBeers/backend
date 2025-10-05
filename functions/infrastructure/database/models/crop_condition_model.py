from infrastructure.database.interface.model_interface import ModelInterface


class CropConditionModel(ModelInterface):
    crop_name: str
    temperature: float  # °C
    humidity: float  # %
    root_soil_moisture: float  # 0-1
    top_soil_moisture: float  # 0-1
    soil_temperature: float  # °C
    snow_precipitation: float  # mm/day
    rain_precipitation: float  # mm/day
