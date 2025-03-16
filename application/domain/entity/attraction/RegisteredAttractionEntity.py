class RegisteredAttractionEntity:
    def __init__(self, id, order, tags, cost, rating):
        self.id = id
        self.order = order
        self.tags = tags
        self.cost = cost
        self.rating = rating
        self.smart_score = None
