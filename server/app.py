import os
from flask import Flask, request, jsonify
import sqlite3
import datetime
from model import getResult, refresh_data
import random

app = Flask(__name__)


# Connect to the database file
# Create tables if they have not already
if not os.path.exists("database.db"):
    with sqlite3.connect("database.db") as connect:
        connect.execute("""
        CREATE TABLE IF NOT EXISTS PitchEntries (
            pitchEntryID INTEGER PRIMARY KEY AUTOINCREMENT,
            pitcherHandedness TEXT NOT NULL,
            batterHandedness TEXT NOT NULL,
            pitchType TEXT NOT NULL,
            velocity REAL NOT NULL,
            horizontalBreak REAL NOT NULL,
            verticalBreak REAL NOT NULL,
            zone INTEGER NOT NULL,
            balls INTEGER NOT NULL,
            strikes INTEGER NOT NULL
        );
        """)
        connect.execute("""
        CREATE TABLE IF NOT EXISTS Predictions (
            predictionID INTEGER PRIMARY KEY AUTOINCREMENT,
            result TEXT NOT NULL,
            contactprob TEXT NOT NULL,
            strikeprob TEXT NOT NULL,
            ballprob TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            pitchEntryID INTEGER NOT NULL,
            FOREIGN KEY (pitchEntryID) REFERENCES PitchEntries(pitchEntryID)
        );
        """)


# Defualt endpoint
@app.route('/')
def home():
    return "Flask app is running!", 200

# Endpoint: Add a new pitch entry
@app.route('/add_pitch_entry', methods=['POST'])
def add_pitch_entry():
    data = request.json
    pitcher_handedness = data.get('pitcherHandedness')
    batter_handedness = data.get('batterHandedness')
    pitch_type = data.get('pitchType')
    velocity = data.get('velocity')
    break_horizontal = data.get('horizontalBreak')
    break_vertical = data.get('verticalBreak')
    zone = data.get('zone')
    balls = data.get('balls')
    strikes = data.get('strikes')

    with sqlite3.connect("database.db") as database:
        cursor = database.cursor()
        cursor.execute("""
            INSERT INTO PitchEntries (pitcherHandedness, batterHandedness, pitchType, velocity, horizontalBreak, verticalBreak, zone, balls, strikes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (pitcher_handedness, batter_handedness, pitch_type, velocity, break_horizontal, break_vertical, zone, balls, strikes))
        database.commit()

    pitch_entry_id = cursor.lastrowid

    # Use ML model to create prediction
    pitch_input = [velocity, zone, break_horizontal, break_vertical, balls, strikes]
    prediction = getResult(pitch_input)

    # Convert 2d array into dictionary
    labels = ['ball', 'contact', 'strike']
    probabilities = {label: float(val) for label, val in zip(labels, prediction.flatten())}

    # Use probabilities to get a random result of pitch
    outcomes = list(probabilities.keys())
    values = list(probabilities.values())
    result = random.choices(outcomes, weights=values, k=1)[0]
    print(probabilities)
    print(result)

    # Insert prediction into Predictions database
    timestamp = datetime.datetime.now()
    with sqlite3.connect("database.db") as database:
        cursor = database.cursor()
        cursor.execute("""
            INSERT INTO Predictions (result, contactprob, strikeprob, ballprob, timestamp, pitchEntryID)
            VALUES (?, ?, ?, ?, ?, ?)        
        """, (result, probabilities["contact"], probabilities["strike"], probabilities["ball"], datetime.datetime.now(), pitch_entry_id))
        database.commit()

    return jsonify({
        'message': 'Pitch entry added and prediction made successfully!',
        'pitchEntryID': pitch_entry_id,
        'prediction': {'result': result, 'probabilities': probabilities}
    })


# Endpoint: Get prediction history
@app.route('/get_history', methods=['GET'])
def get_history():
    try:
        # Open a connection and execute the query
        with sqlite3.connect("database.db") as connect:
            cursor = connect.cursor()
            cursor.execute("""
                SELECT p.predictionID, p.result, p.contactprob, p.strikeprob, p.ballprob, p.timestamp, pe.pitcherHandedness,
                    pe.batterHandedness, pe.pitchType, pe.velocity, pe.horizontalBreak, pe.verticalBreak, pe.zone, pe.balls, pe.strikes
                FROM Predictions p
                JOIN PitchEntries pe ON p.pitchEntryID = pe.pitchEntryID            
            """, ())
            entries = cursor.fetchall()

        # Check if a result was found
        if entries:
            # Create a dictionary for the output
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in entries]

            return jsonify(results)
        else:
            return jsonify({'error': 'Prediction not found'}), 404
    except sqlite3.Error as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500


# Endpoint: Clear prediction history
@app.route('/clear_history', methods=['POST'])
def clear_history():
    with sqlite3.connect("database.db") as database:
        cursor = database.cursor()
        cursor.execute("DELETE FROM Predictions")
        database.commit()

    return jsonify({'message': 'Prediction history cleared!'})

# Intialize and train model
refresh_data()

# Run the Flask server locally
if __name__ == '__main__':

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))