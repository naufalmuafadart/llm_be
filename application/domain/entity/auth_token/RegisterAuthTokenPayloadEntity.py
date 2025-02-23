from bson import ObjectId

class RegisterAuthTokenPayloadEntity:
    def __init__(self, id):
        self.id = id
        self.exp = None
        if isinstance(self.id, str):
            self.id = ObjectId(self.id)
