from pymongo import MongoClient
import json

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')

# Create or connect to a database
db = client['tracking_db']

# Create or connect to a collection
collection = db['trackers']

tracker_id = '1'
result = collection.find_one({'tracker_id': tracker_id})
print(f"Tracker {tracker_id}: {result}")
