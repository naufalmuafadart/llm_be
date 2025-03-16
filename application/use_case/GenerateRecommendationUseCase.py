from datetime import timedelta, datetime
from application.domain.entity.itinerary_request.RequestKeyDetailEntity import RequestKeyDetailEntity
import time

class GenerateRecommendationUseCase:
    def __init__(self, data_frame_repository, algorithm_repository, llm_repository, attraction_repository, attraction_ranking_repository):
        self.data_frame_repository = data_frame_repository
        self.algorithm_repository = algorithm_repository
        self.llm_repository = llm_repository
        self.attraction_repository = attraction_repository
        self.attraction_ranking_repository = attraction_ranking_repository

    def execute(self, message):
        high_rating_doi_keyword = [
            'populer',
            'popular',
            'bahagia',
            'terkenal'
        ]

        df_places = self.data_frame_repository.get_data('places')

        # extract key detail from the message
        content = "This is an itinerary request in Bahasa. Please extract the days count, preffered attraction type, and preferred budget. Show the data in json format. The name of each key in json is `days_count`, `preferred_attraction`, and `preferred_budget`. The `preferred_attraction` should be serve as array. If the key detail is not exist, set the value to null. \""+message+"\""
        data = self.llm_repository.get_request_key_detail(content)
        print(data)
        # data = {'days_count': 2, 'preferred_attraction': ['alam', 'instagramable'], 'preferred_budget': 'murah'}

        n_day = data['days_count'] # Get #day from extracted data
        if n_day is None: # if day is none
            n_day = 1

        # get preferred attraction
        preferred_attraction = data['preferred_attraction']
        if preferred_attraction is None or len(preferred_attraction) == 0:
            raise Exception('Cannot generate itinerary without preferred attraction')

        # get id of attraction based on preferred attraction
        selected_ids = self.attraction_repository.get_ids_by_selected_tags(preferred_attraction)
        if selected_ids is None or len(selected_ids) == 0:
            raise Exception('Cannot generate itinerary without preferred attraction')

        doi_cost = 0.5
        preferred_budget = data['preferred_budget']
        if preferred_budget == 'murah' or preferred_budget == 'terjangkau' or preferred_budget == 'budgetfriendly' or preferred_budget == 'budget friendly':
            doi_cost = 1
        
        doi_rating = 0.5
        if any(keyword in message.lower() for keyword in high_rating_doi_keyword):
            doi_rating = 1

        registered_attractions = self.attraction_repository.get_registered_attraction_by_ids(selected_ids) # get attraction data from db
        registered_attractions = self.attraction_ranking_repository.sort_attraction(registered_attractions, doi_rating, doi_cost) # sort attraction using AHP
        registered_attractions = registered_attractions[:n_day*6]

        selected_ids = [attraction.order for attraction in registered_attractions]

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
