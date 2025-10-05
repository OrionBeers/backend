
from pydantic import Field
from bson.objectid import ObjectId

from functions.infrastructure.database.interface.model_interface import ModelInterface

class DashboardDataModel(ModelInterface):
    id: str = Field(alias="_id", default_factory=lambda: str(ObjectId()))
    id_user: str
    crop: str
    date_range: dict
    calendar: dict