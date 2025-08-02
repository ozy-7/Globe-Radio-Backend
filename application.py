from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# Load radio stations from the JSON file
with open("bulk_stations.json", "r") as f:
    lines = f.readlines()
    # Only parse the data lines
    stations = [json.loads(lines[i]) for i in range(1, len(lines), 2)]

@app.route("/")
def home():
    return "Globe Radio API is running!"

@app.route("/search")
def search():
    query = request.args.get("q", "").lower()
    keywords = query.split()

    if not keywords:
        return jsonify([])

    # Match if all keywords exist in the station fields
    def matches(station):
        combined = f"{station.get('name', '')} {station.get('tags', '')} {station.get('country', '')}".lower()
        return all(k in combined for k in keywords)

    results = [s for s in stations if matches(s)]
    return jsonify(results[:100])  # Limit to first 100 results for performance

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use PORT from environment if available
    app.run(host="0.0.0.0", port=port)
