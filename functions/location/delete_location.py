from infrastructure.database.collections.locations_collection import LocationsCollection


class LocationDelete:
    def __init__(self, user_id: str):
        self.user_id = user_id

    def execute(self, id: str):
        location = LocationsCollection().get_one(
            filter_by={"id": id, "user_id": self.user_id},
            hidden_fields=[],
            force_show_fields=[],
        )
        if not location:
            raise Exception("Location not found")

        LocationsCollection().delete_one(filter_by={"id": id, "user_id": self.user_id})
        return {"message": "Location deleted successfully"}
