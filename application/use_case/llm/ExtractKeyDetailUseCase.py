# entity
from application.domain.entity.itinerary_request.RequestKeyDetailEntity import RequestKeyDetailEntity

class ExtractKeyDetailUseCase:
    def __init__(self, llm_repository):
        self.llm_repository = llm_repository
    
    def execute(self, message):
        content = "This is an itinerary request in Bahasa. Please extract the days count, preffered attraction type, and preferred budget. Show the data in json format. The name of each key in json is `days_count`, `preferred_attraction`, and `preferred_budget`. The `preferred_attraction` should be serve as array. If the key detail is not exist, set the value to null. \""+message+"\""
        data = self.llm_repository.get_request_key_detail(content)
        key_details = RequestKeyDetailEntity(
            data['days_count'],
            data['preferred_attraction'],
            data['preferred_budget'],
        )
        return key_details.get_output()
