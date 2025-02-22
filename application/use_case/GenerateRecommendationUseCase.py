from datetime import timedelta, datetime
import time

class GenerateRecommendationUseCase:
    def __init__(self, data_frame_repository, algorithm_repository):
        self.data_frame_repository = data_frame_repository
        self.algorithm_repository = algorithm_repository

    def execute(self, message):
        df_places = self.data_frame_repository.get_data('places')

        n_day = int(message[25])
        selected_ids = message[65:]
        selected_ids = selected_ids.split(',')
        selected_ids = [int(item.strip()) for item in selected_ids]

        output, Fbest = self.algorithm_repository.construct_solution(
            selected_ids,
            129, # id hotel
            1, # doi duration
            1, # doi cost
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
