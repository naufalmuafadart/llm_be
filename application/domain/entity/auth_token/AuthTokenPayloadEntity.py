from bson import ObjectId

class AuthTokenPayloadEntity:
    def __init__(self, id, exp):
        self.id = id
        self.exp = exp
        if isinstance(self.id, str):
            self.id = ObjectId(self.id)
