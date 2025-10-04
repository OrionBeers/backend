from infrastructure.database.collections.users_collection import UsersCollection


class UserDetails:
    def __init__(self, email):
        self.email = email

    def execute(self):
        user =  UsersCollection().get_one(filter_by={"email": self.email}, hidden_fields=[], force_show_fields=[])
        if not user:
            raise Exception("User not found")

        return user
