from infrastructure.database.collections.locations_collection import LocationsCollection
from infrastructure.database.models.location_model import LocationModel


class LocationCreate:
    def __init__(
        self,
        user_id: str,
        display_name: str = None,
        latitude: float = None,
        longitude: float = None,
    ):
        self.user_id = user_id
        self.display_name = display_name
        self.latitude = latitude
        self.longitude = longitude

    def execute(self):
        location = {
            "display_name": self.display_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "user_id": self.user_id,
        }
        LocationsCollection().insert(LocationModel(**location))
        print(f"Location created with name: {self.display_name}")
        return {"display_name": self.display_name, "status": "created"}
