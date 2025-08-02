from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from search_utils import search_stations

app = Flask(__name__)
CORS(app)

# Load stations once on startup
with open("bulk_stations.json", "r", encoding="utf-8") as f:
    lines = f.readlines()
    stations = [json.loads(lines[i]) for i in range(1, len(lines), 2)]

@app.route("/")
def home():
    return "Globe Radio API is running!"

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])

    results = search_stations(query, stations)
    return jsonify(results)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
