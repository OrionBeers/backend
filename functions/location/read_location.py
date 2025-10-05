from typing import Optional

from infrastructure.database.collections.locations_collection import LocationsCollection


class LocationDetails:
    def __init__(self, id_user: str):
        self.id_user = id_user

    def execute(self, id_location: Optional[str] = None):

        if id_location is None:
            location = LocationsCollection().list(
                filter_by={"id_user": self.id_user},
                hidden_fields=[],
                force_show_fields=[],
            )

        else:
            location = LocationsCollection().get_one(
                filter_by={"_id": id_location, "id_user": self.id_user},
                hidden_fields=[],
                force_show_fields=[],
            )


        if not location:
            raise Exception("Location not found")

        return location
