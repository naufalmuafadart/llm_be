from application.domain.repository.AttractionRepository import AttractionRepository
from application.infrastructure.database.mongo_db import MongoDBClient
from application.domain.entity.attraction.RegisteredAttractionEntity import RegisteredAttractionEntity

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

    def get_registered_attraction_by_ids(self, ids):
        client = MongoDBClient()
        db = client.get_database()
        attractions_collection = db["attractions"]

        attractions = list(attractions_collection.aggregate([
            {
                "$lookup": {
                    "from": "places",
                    "localField": "place_id",
                    "foreignField": "_id",
                    "as": "place_info"
                }
            },
            {
                "$match": {
                    "place_info.order": {"$in": ids}
                }
            },
            {
                "$set": {
                    "rating": {"$arrayElemAt": ["$place_info.rating", 0]},
                    "order": {"$arrayElemAt": ["$place_info.order", 0]},
                }
            },
            {
                "$unset": "place_info"
            }
        ]))

        results = []
        for attr in attractions:
            results.append(RegisteredAttractionEntity(
                str(attr['_id']),
                attr['order'],
                attr['tags'],
                attr['cost'],
                attr['rating'],
            ))

        return results
