class RequestKeyDetailEntity:
    def __init__(self, days_count, preferred_attraction, preferred_budget):
        self.days_count = days_count
        self.preferred_attraction = preferred_attraction
        self.preferred_budget = preferred_budget
    
    def get_output(self):
        return {
            'days_count': self.days_count,
            'preferred_attraction': self.preferred_attraction,
            'preferred_budget': self.preferred_budget,
        }
