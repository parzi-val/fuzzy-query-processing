from pymongo import MongoClient
import json

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')

# Create or connect to a database
db = client['tracking_db']

# Create or connect to a collection
collection = db['trackers']

# Load data from the JSON file
with open('output.json', 'r') as file:
    data = json.load(file)

# Convert JSON data to MongoDB documents
documents = [{'tracker_id': key, **value} for key, value in data.items()]

# Insert documents into the collection
collection.insert_many(documents)

print("Documents inserted successfully")
