from application.domain.repository.AttractionRepository import AttractionRepository
from application.infrastructure.database.mongo_db import MongoDBClient

class MongoAttractionRepository(AttractionRepository):
    def get_ids_by_selected_tags(self, tags):
        client = MongoDBClient()
        db = client.get_database()
        attractions_collection = db["attractions"]
        places_collection = db["places"]

        pipeline = [
            # Step 1: Filter attractions that contain all specified tags
            {"$match": {"tags": {"$in": tags}}},

            # Step 2: Join with places collection
            {
                "$lookup": {
                    "from": "places",         # Collection to join
                    "localField": "place_id", # Field in attractions collection
                    "foreignField": "_id",    # Field in places collection
                    "as": "place_details"     # Output field name
                }
            },

            # Step 3: Unwind the array (if needed)
            {"$unwind": "$place_details"},

            # Step 4: Select fields to return
            {
                "$project": {
                    "_id": 0,  # Exclude attraction _id
                    "tags": 1,
                    "place_details.order": 1,
                }
            }
        ]

        # Execute query
        results = attractions_collection.aggregate(pipeline)

        ids = []
        for result in results:
            ids.append(result['place_details']['order'])

        return ids