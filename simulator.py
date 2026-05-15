from pymongo import MongoClient
from datetime import datetime
import random
import time
import math
import os
from flask import Flask
from threading import Thread

# ---------------------------
# Flask app (Render requires open port)
# ---------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Drone simulator running"

# ---------------------------
# MongoDB connection
# ---------------------------
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    print("ERROR: MONGO_URI not set")

client = MongoClient(MONGO_URI)

db = client["drone_monitoring"]
collection = db["drone_telemetry"]

# ---------------------------
# Tokyo coordinates
# ---------------------------
TOKYO_LAT = 35.6764
TOKYO_LON = 139.6500

# Reset every 15 minutes
RESET_INTERVAL = 900

# ---------------------------
# Drone setup
# ---------------------------
def create_initial_drones():
    return [
        {"drone_id": "DR001", "lat": 36.5000, "lon": 141.2000, "speed": 120},
        {"drone_id": "DR002", "lat": 35.9000, "lon": 140.8000, "speed": 100},
        {"drone_id": "DR003", "lat": 36.1000, "lon": 140.3000, "speed": 140}
    ]

def calculate_distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) * 111

# ---------------------------
# Simulator
# ---------------------------
def run_simulator():

    print("Simulator started...")

    drones = create_initial_drones()
    start_time = time.time()

    while True:

        try:

            # Reset every 15 minutes
            if time.time() - start_time > RESET_INTERVAL:
                print("Resetting system...")
                collection.delete_many({})
                drones = create_initial_drones()
                start_time = time.time()

            for drone in drones:

                drone["lat"] += (TOKYO_LAT - drone["lat"]) * 0.01
                drone["lon"] += (TOKYO_LON - drone["lon"]) * 0.01

                drone["speed"] += random.uniform(-2, 2)
                if drone["speed"] < 50:
                    drone["speed"] = 50

                distance = calculate_distance(
                    drone["lat"],
                    drone["lon"],
                    TOKYO_LAT,
                    TOKYO_LON
                )

                eta = (distance / drone["speed"]) * 60

                if distance < 20:
                    threat = "Critical"
                elif distance < 50:
                    threat = "High"
                elif distance < 100:
                    threat = "Medium"
                else:
                    threat = "Low"

                document = {
                    "drone_id": drone["drone_id"],
                    "timestamp": datetime.utcnow(),

                    "latitude": round(drone["lat"], 6),
                    "longitude": round(drone["lon"], 6),

                    "city_target": random.choice(["Tokyo", "Osaka", "Yokohama"]),

                    "speed_kmh": round(drone["speed"], 2),
                    "altitude_m": random.randint(100, 1200),
                    "distance_to_tokyo_km": round(distance, 2),
                    "eta_minutes": round(eta, 2),

                    "threat_level": threat,
                    "threat_score": random.randint(1, 100),
                    "payload_risk": random.randint(1, 10),
                    "restricted_zone": random.choice([True, False]),

                    "drone_type": random.choice([
                        "Commercial",
                        "Unknown",
                        "Military",
                        "Hobby",
                        "Autonomous"
                    ]),

                    "signal_strength": random.randint(60, 100),
                    "battery_level": random.randint(20, 100),

                    "detection_confidence": round(random.uniform(70, 99), 2),
                    "response_time_sec": random.randint(10, 300),

                    "intercept_status": random.choice([
                        "Monitoring",
                        "Tracking",
                        "Intercepted",
                        "Escaped"
                    ])
                }

                try:
                    result = collection.insert_one(document)
                    print("Inserted:", drone["drone_id"], result.inserted_id)
                except Exception as e:
                    print("Mongo Insert Error:", e)

            time.sleep(1)

        except Exception as e:
            print("Simulator Error:", e)
            time.sleep(2)

# ---------------------------
# Start background thread (SAFE for Render)
# ---------------------------
def start_simulator():
    thread = Thread(target=run_simulator)
    thread.daemon = True
    thread.start()

start_simulator()

# ---------------------------
# Render Web Port
# ---------------------------
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)