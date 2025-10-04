from datetime import datetime
from pydantic import Field
from bson.objectid import ObjectId

from infrastructure.database.interface.model_interface import ModelInterface


class UsersModel(ModelInterface):
    id: str = Field(alias="_id", default_factory=lambda: str(ObjectId()))
    name: str
    email: str
    id_google: str
    avatar: str = None

    ## Historical data after first research
    historical_data: list[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())

