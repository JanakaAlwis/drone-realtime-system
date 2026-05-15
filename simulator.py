from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError
from datetime import datetime
import random
import time
import math
import os
from flask import Flask
from threading import Thread

# ---------------------------
# Flask (Render requires open port)
# ---------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Drone simulator running (PROD SAFE)"

# ---------------------------
# MongoDB (PRODUCTION SAFE)
# ---------------------------
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
    retryWrites=True
)

db = client["drone_monitoring"]
collection = db["drone_telemetry"]

# ---------------------------
# CONFIG (production control)
# ---------------------------
TOKYO_LAT = 35.6764
TOKYO_LON = 139.6500

RESET_INTERVAL = 900
WRITE_INTERVAL = 2  # IMPORTANT: reduce load (was 1 sec)

# ---------------------------
# DRONES
# ---------------------------
def create_initial_drones():
    return [
        {"drone_id": "DR001", "lat": 36.5000, "lon": 141.2000, "speed": 120},
        {"drone_id": "DR002", "lat": 35.9000, "lon": 140.8000, "speed": 100},
        {"drone_id": "DR003", "lat": 36.1000, "lon": 140.3000, "speed": 140}
    ]

def calculate_distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111

# ---------------------------
# SAFE INSERT FUNCTION
# ---------------------------
def safe_insert(document):
    try:
        result = collection.insert_one(document)
        print("Inserted:", document["drone_id"], result.inserted_id)
    except (ServerSelectionTimeoutError, PyMongoError) as e:
        print("MongoDB Insert Failed:", e)
        time.sleep(2)  # small backoff before retry

# ---------------------------
# SIMULATOR LOOP (PRODUCTION SAFE)
# ---------------------------
def run_simulator_forever():
    print("Simulator started...")

    drones = create_initial_drones()
    start_time = time.time()

    while True:
        try:

            for drone in drones:

                drone["lat"] += (TOKYO_LAT - drone["lat"]) * 0.01
                drone["lon"] += (TOKYO_LON - drone["lon"]) * 0.01

                drone["speed"] += random.uniform(-2, 2)
                if drone["speed"] < 50:
                    drone["speed"] = 50

                distance = calculate_distance(
                    drone["lat"], drone["lon"],
                    TOKYO_LAT, TOKYO_LON
                )

                eta = (distance / drone["speed"]) * 60

                collection.insert_one({
                    "drone_id": drone["drone_id"],
                    "timestamp": datetime.utcnow(),
                    "latitude": drone["lat"],
                    "longitude": drone["lon"],
                    "speed_kmh": drone["speed"],
                    "distance_to_tokyo_km": distance,
                    "eta_minutes": eta
                })

                print("Inserted:", drone["drone_id"])

            time.sleep(2)

        except Exception as e:
            print("Error:", e)
            time.sleep(3)


# IMPORTANT: start simulator BEFORE Flask blocks
from threading import Thread
Thread(target=run_simulator_forever, daemon=True).start()

port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)