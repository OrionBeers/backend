from infrastructure.database.collections.users_collection import UsersCollection


class UserUpdate:
    def __init__(self, email, name=None, avatar=None, is_onboarding=None):
        self.email = email
        self.name = name
        self.avatar = avatar
        self.is_onboarding = is_onboarding

    def execute(self):
        user = UsersCollection().get_one(filter_by={"email": self.email}, hidden_fields=[], force_show_fields=[])
        if not user:
            raise Exception("User not found")

        update_data = {}
        if self.name is not None:
            update_data["name"] = self.name
        if self.avatar is not None:
            update_data["avatar"] = self.avatar
        if self.is_onboarding is not None:
            update_data["is_onboarding"] = self.is_onboarding

        if update_data:
            UsersCollection().update(
                filter_by={"email": self.email},
                data_to_update=update_data
            )
            user = UsersCollection().get_one(filter_by={"email": self.email}, hidden_fields=[], force_show_fields=[])
            return user

        return user
