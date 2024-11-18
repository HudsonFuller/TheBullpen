from flask import Flask, request, jsonify
import sqlite3
import datetime

app = Flask(__name__)


# Connect to the database file
# Create tables if they have not already
connect = sqlite3.connect('database.db')
connect.execute("""
CREATE TABLE IF NOT EXISTS PitchEntries (
    pitchEntryID INTEGER PRIMARY KEY AUTOINCREMENT,
    pitchType TEXT NOT NULL,
    velocity REAL NOT NULL,
    spinRate REAL NOT NULL,
    breakHorizontal REAL NOT NULL,
    breakVertical REAL NOT NULL,
    zone INTEGER NOT NULL
);
""")
connect.execute("""
CREATE TABLE IF NOT EXISTS Predictions (
    predictionID INTEGER PRIMARY KEY AUTOINCREMENT,
    result TEXT NOT NULL,
    hitintopplayprob TEXT NOT NULL,
    strikeprob TEXT NOT NULL,
    ballprob TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    pitchEntryID INTEGER NOT NULL,
    FOREIGN KEY (pitchEntryID) REFERENCES PitchEntries(pitchEntryID)
);
""")


# Endpoint: Add a new pitch entry
@app.route('/add_pitch_entry', methods=['POST'])
def add_pitch_entry():
    data = request.json
    pitch_type = data.get('pitchType')
    velocity = data.get('velocity')
    spin_rate = data.get('spinRate')
    break_horizontal = data.get('breakHorizontal')
    break_vertical = data.get('breakVertical')
    zone = data.get('zone')

    with sqlite3.connect("database.db") as database:
        cursor = database.cursor()
        cursor.execute("""
            INSERT INTO PitchEntries (pitchType, velocity, spinRate, breakHorizontal, breakVertical, zone)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (pitch_type, velocity, spin_rate, break_horizontal, break_vertical, zone))
        database.commit()

    return jsonify({'message': 'Pitch entry added successfully!'})


# Endpoint: Make a prediction
@app.route('/make_prediction', methods=['POST'])
def make_prediction():
    data = request.json
    pitch_entry_id = data.get('pitchEntryID')
    
    # Simulate prediction logic (replace with ML model logic)
    result = "strike"  # Example result
    probabilities = {"strike": 0.7, "ball": 0.2, "hit": 0.1}  # Example probabilities

    timestamp = datetime.datetime.now()
    with sqlite3.connect("database.db") as database:
        cursor = database.cursor()
        cursor.execute("""
            INSERT INTO Predictions (result, hitintopplayprob, strikeprob, ballprob, timestamp, pitchEntryID)
            VALUES (?, ?, ?, ?, ?, ?)        
        """, (result, probabilities["hit"], probabilities["strike"], probabilities["ball"], datetime.datetime.now(), pitch_entry_id))
        database.commit()

    return jsonify({'message': 'Prediction made successfully!', 'result': result, 'probabilities': probabilities})


# Endpoint: Get prediction history
@app.route('/get_history/<int:predictionID>', methods=['GET'])
def get_history(predictionID):
    try:
        # Open a connection and execute the query
        with sqlite3.connect("database.db") as connect:
            cursor = connect.cursor()
            cursor.execute("""
                SELECT p.predictionID, p.result, p.hitintopplayprob, p.strikeprob, p.ballprob, p.timestamp,
                    pe.pitchType, pe.velocity, pe.spinRate, pe.breakHorizontal, pe.breakVertical, pe.zone
                FROM Predictions p
                JOIN PitchEntries pe ON p.pitchEntryID = pe.pitchEntryID
                WHERE p.predictionID = ?
            """, (predictionID,))
            entry = cursor.fetchone()

        # Check if a result was found
        if entry:
            # Create a dictionary for the output
            columns = [desc[0] for desc in cursor.description]
            return jsonify(dict(zip(columns, entry)))
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


# Run the Flask server
if __name__ == '__main__':
    app.run(debug=True)