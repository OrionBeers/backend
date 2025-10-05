
from datetime import datetime
from typing import Literal

from pydantic import Field
from bson.objectid import ObjectId

from infrastructure.database.interface.model_interface import ModelInterface


class RequestModel(ModelInterface):
    id: str = Field(alias="_id", default_factory=lambda: str(ObjectId()))
    id_user: str
    status: Literal["pending", "processing", "completed", "failed"] = "pending"

    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
