
from datetime import datetime
from pydantic import Field
from bson.objectid import ObjectId

from src.infrastructure.database.interface.model_interface import ModelInterface


class SampleModel(ModelInterface):
    id: str = Field(alias="_id", default_factory=lambda: str(ObjectId()))
    description: str = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())

