from datetime import datetime
from pydantic import Field
from bson.objectid import ObjectId

from infrastructure.database.interface.model_interface import ModelInterface

class LocationModel(ModelInterface):
    id: str = Field(alias="_id", default_factory=lambda: str(ObjectId()))
    displayName: str
    latitude: float
    longitude: float
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
