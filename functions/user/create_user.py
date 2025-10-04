from infrastructure.database.collections.users_collection import UsersCollection
from infrastructure.database.models.user_model import UsersModel


class CreateUser:
    def __init__(self, email, avatar, name, uid):
        self.email = email
        self.avatar = avatar
        self.name = name
        self.uid = uid

    def execute(self):
        user = {
            "email": self.email,
            "avatar": self.avatar,
            "name": self.name,
            "id_google": self.uid,
        }
        UsersCollection().insert(UsersModel(**user))

        print(f"User created with email: {self.email}")
        return {"email": self.email, "status": "created"}