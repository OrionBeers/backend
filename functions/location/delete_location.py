from infrastructure.database.collections.locations_collection import LocationsCollection


class LocationDelete:
    def __init__(self, id_user:str, id_location: str):
        self.id_user = id_user
        self.id_location = id_location

    def execute(self):
        location = LocationsCollection().get_one(
            filter_by={"_id": self.id_location, "id_user": self.id_user},
            hidden_fields=[],
            force_show_fields=[],
        )
        if not location:
            raise Exception("Location not found")

        LocationsCollection().delete(filter_by={"_id": self.id_location, "id_user": self.id_user})
        return {"message": "Location deleted successfully"}
