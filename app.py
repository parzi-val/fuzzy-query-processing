from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient
import os
from FuzzyQuerying import FuzzyEngine  # Import the FuzzyEngine

app = Flask(__name__)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['tracking_db']
collection = db['trackers']

# Initialize FuzzyEngine
fuzzy_engine = FuzzyEngine(client)

# Configurations
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Route to upload video
@app.route('/', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST':
        file = request.files['video']
        if file and file.filename.endswith('.mp4'):
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            # Process video
            # processed_data = process_video(file_path)
            
            # # Save processed data to MongoDB
            # collection.insert_one(processed_data)

            return redirect(url_for('results'))

    return render_template('upload.html')

# Route to show results
@app.route('/results', methods=['GET'])
def results():
    query = request.args.get('query')

    if query:
        subject, action, attribute, fuzzy_value = fuzzy_engine.parse_natural_language_query(query)
        fuzzy_set = fuzzy_engine.map_fuzzy_value_to_set(fuzzy_value)
        results = fuzzy_engine.execute_fuzzy_query(fuzzy_set)
    else:
        results = []

    return render_template('results.html', data=results)

def process_video(file_path):
    # Replace this with actual video processing logic
    # Here, we simulate it with a placeholder dictionary
    return {
        'tracker_id': '1',  # Placeholder data
        'distance': 750.236,  # Placeholder data
        'speed': 18755.902  # Placeholder data
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
