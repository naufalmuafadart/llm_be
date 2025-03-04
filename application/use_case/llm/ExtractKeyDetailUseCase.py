class ExtractKeyDetailUseCase:
    def __init__(self, llm_repository):
        self.llm_repository = llm_repository
    
    def execute(self, message):
        data = self.llm_repository.get_request_key_detail(message)
        return data