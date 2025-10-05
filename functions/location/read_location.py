from typing import Optional

from infrastructure.database.collections.locations_collection import LocationsCollection


class LocationDetails:
    def __init__(self, user_id: str):
        self.user_id = user_id

    # Read one location by id
    def execute(self, id: Optional[str] = None):
        location = LocationsCollection().get_all(
            filter_by={"id": id, "user_id": self.user_id},
            hidden_fields=[],
            force_show_fields=[],
        )
        if not location:
            raise Exception("Location not found")

        return location
