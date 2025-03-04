from datetime import timedelta, datetime
from application.domain.entity.itinerary_request.RequestKeyDetailEntity import RequestKeyDetailEntity
import time

class GenerateRecommendationUseCase:
    def __init__(self, data_frame_repository, algorithm_repository, llm_repository, attraction_repository):
        self.data_frame_repository = data_frame_repository
        self.algorithm_repository = algorithm_repository
        self.llm_repository = llm_repository
        self.attraction_repository = attraction_repository

    def execute(self, message):
        df_places = self.data_frame_repository.get_data('places')

        # extract key detail from the message
        content = "This is an itinerary request in Bahasa. Please extract the days count, preffered attraction type, and preferred budget. Show the data in json format. The name of each key in json is `days_count`, `preferred_attraction`, and `preferred_budget`. The `preferred_attraction` should be serve as array. If the key detail is not exist, set the value to null. \""+message+"\""
        data = self.llm_repository.get_request_key_detail(content)

        n_day = data['days_count']
        if n_day is None:
            n_day = 1

        selected_ids = [1, 2, 3, 4, 5]
        preferred_attraction = data['preferred_attraction']
        if preferred_attraction is None or len(preferred_attraction) == 0:
            raise Exception('Cannot generate itinerary without preferred attraction')

        selected_ids = self.attraction_repository.get_ids_by_selected_tags(preferred_attraction)
        if selected_ids is None or len(selected_ids) == 0:
            raise Exception('Cannot generate itinerary without preferred attraction')
        
        doi_cost = 0.3
        preferred_budget = data['preferred_budget']
        if preferred_budget == 'murah' or preferred_budget == 'terjangkau' or preferred_budget == 'budgetfriendly' or preferred_budget == 'budget friendly':
            doi_cost = 1

        output, Fbest = self.algorithm_repository.construct_solution(
            selected_ids,
            129, # id hotel
            1, # doi duration
            doi_cost, # doi cost
            1, # doi rating
            n_day,
            1
        )

        content = [
            {
                'element': 'text',
                'text': f'Berikut ini rute wisata dalam {n_day} hari',
            },
        ]

        for i in range(n_day):
            content.append({
                'element': 'heading',
                'level': 1,
                'text': f'Hari ke-{i + 1}',
            })

            route = output[0]['results'][i]

            children = []
            for j in range(len(route['index'])):
                beginning_time = route['waktu'][j+1]
                name = df_places[df_places['id'] == route['index'][j]].iloc[0]['name']
                duration = df_places[df_places['id'] == route['index'][j]].iloc[0]['durasi']
                _t = time.strptime(beginning_time, "%H:%M:%S")
                date_time = datetime(2023, 1, 1, _t.tm_hour, _t.tm_min, _t.tm_sec)
                date_time_end = date_time + timedelta(seconds=int(duration))
                children.append({
                    'type': 'text',
                    'text': f"{name} ({date_time.strftime('%H.%M')}-{date_time_end.strftime('%H.%M')})",
                })

            content.append({
                'element': 'list',
                'type': 'unordered',
                'children': children
            })

        return content
