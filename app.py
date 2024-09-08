from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient
import os

app = Flask(__name__)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['tracking_db']
collection = db['trackers']

# Configurations
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Speed and distance ranges
SPEED_RANGES = {
    'slow': (0, 1000),
    'medium': (1000, 6000),
    'fast': (6000, float('inf'))
}

DISTANCE_RANGES = {
    'short': (0, 30),
    'medium': (30, 100),
    'long': (100, float('inf'))
}

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
    tracker_id = request.args.get('tracker_id')
    speed_category = request.args.get('speed_category')
    distance_category = request.args.get('distance_category')
    distance_range = None
    speed_range = None

    query = {}
    
    if tracker_id:
        query['tracker_id'] = tracker_id
    
    if speed_category and speed_category in SPEED_RANGES:
        min_speed, max_speed = SPEED_RANGES[speed_category]
        query['speed'] = {'$gte': min_speed, '$lte': max_speed}
        speed_range = (min_speed, max_speed)
    
    if distance_category and distance_category in DISTANCE_RANGES:
        min_distance, max_distance = DISTANCE_RANGES[distance_category]
        query['distance'] = {'$gte': min_distance, '$lte': max_distance}
        distance_range = (min_distance, max_distance)

    data = collection.find(query).limit(30) 
    
    return render_template('results.html', data=data, speed_range=speed_range, distance_range=distance_range)

def process_video(file_path):
    # Replace this with actual video processing logic
    # Here, we simulate it with a placeholder dictionary
    return {
        'tracker_id': '1',  # Placeholder data
        'distance': 750.236,  # Placeholder data
        'speed': 18755.902  # Placeholder data
    }

if __name__ == '__main__':
    app.run(debug=True)
