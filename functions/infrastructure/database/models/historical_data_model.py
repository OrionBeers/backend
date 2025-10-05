from datetime import datetime
from pydantic import Field
from bson.objectid import ObjectId

from functions.infrastructure.database.interface.model_interface import ModelInterface

class HistoricalDataModel(ModelInterface):
    id: str = Field(alias="_id", default_factory=lambda: str(ObjectId()))
    id_user: str
    id_request: str

    ## Front-end fields
    latitude: float
    longitude: float
    start_date: datetime
    end_date: datetime
    crop_types: str

    ## OpenAI fields
    best_condition: dict
    timestamps: list[dict]

    step_block: int

    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
