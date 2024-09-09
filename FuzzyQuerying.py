import spacy
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from pymongo import MongoClient


class FuzzyEngine:

    def __init__(self, client):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['tracking_db']  # Assuming your database is named 'player_database'
        self.collection = self.db['trackers'] # Assuming your collection is named 'player_data'

        self.nlp = spacy.load('en_core_web_sm')

        # Fuzzy variable for speed
        self.speed = ctrl.Antecedent(np.arange(0, 101, 1), 'speed')
        self.speed['slow'] = fuzz.trimf(self.speed.universe, [0, 0, 50])
        self.speed['moderate'] = fuzz.trimf(self.speed.universe, [20, 50, 80])
        self.speed['fast'] = fuzz.trimf(self.speed.universe, [50, 100, 100])

    def parse_natural_language_query(self, query):
        doc = self.nlp(query)
        subject, action, attribute, fuzzy_value = "", "", "", ""
        
        for token in doc:
            if token.dep_ == 'nsubj':
                subject = token.text
            elif token.dep_ == 'ROOT':
                action = token.text
            elif token.dep_ == 'attr':
                attribute = token.text
            elif token.pos_ == 'ADJ':
                fuzzy_value = token.text
        
        return subject, action, attribute, fuzzy_value

    def map_fuzzy_value_to_set(self, fuzzy_value):
        if fuzzy_value == 'fast':
            return self.speed['fast']
        elif fuzzy_value == 'moderate':
            return self.speed['moderate']
        elif fuzzy_value == 'slow':
            return self.speed['slow']
        else:
            raise ValueError("Unknown fuzzy value")

    def generate_fuzzy_query(self, attribute, fuzzy_set):
        return f"SELECT object_id, {attribute} FROM player_data WHERE {attribute} IS ABOUT {fuzzy_set};"

    def execute_fuzzy_query(self, fuzzy_set):
        # Query MongoDB for player data, including speed and distance
        player_data = self.collection.find({}, {"tracker_id": 1, "speed": 1, "distance": 1})
        
        matching_results = []
        for data in player_data:
            speed_input = data.get("speed", 0)
            distance_input = data.get("distance", 0)
            
            # Get QCI (Query Compatibility Index) by interpolating the membership
            qci = fuzz.interp_membership(self.speed.universe, fuzzy_set.mf, speed_input)
            
            if qci > 0:
                matching_results.append({
                    "tracker_id": data["tracker_id"],
                    "speed": speed_input,
                    "distance": distance_input,
                    "qci": qci
                })
        
        return sorted(matching_results, key=lambda x: x["qci"], reverse=True)


    def display_results(self, results):
        print("Ranked Query Results:")
        for result in results:
            print(f"Object ID: {result['tracker_id']}, QCI: {result['qci']:.2f}")


# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB connection string

# # Example usage
# engine = FuzzyEngine(client)
# query = "Find players moving at moderate speed"
# subject, action, attribute, fuzzy_value = engine.parse_natural_language_query(query)
# fuzzy_set = engine.map_fuzzy_value_to_set(fuzzy_value)
# results = engine.execute_fuzzy_query(fuzzy_set)
# engine.display_results(results)