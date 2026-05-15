from pymongo import MongoClient
from datetime import datetime
import random
import time
import math
import os

# MongoDB Atlas connection
# MONGO_URI = "mongodb+srv://janaka:Jan123@cluster0.asjsuwa.mongodb.net/?retryWrites=true&w=majority"
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["drone_monitoring"]
collection = db["drone_telemetry"]

# Tokyo coordinates
TOKYO_LAT = 35.6764
TOKYO_LON = 139.6500

# Reset every 15 minutes
RESET_INTERVAL = 900  # seconds

# Function to create initial drones
def create_initial_drones():
    return [
        {
            "drone_id": "DR001",
            "lat": 36.5000,
            "lon": 141.2000,
            "speed": 120
        },
        {
            "drone_id": "DR002",
            "lat": 35.9000,
            "lon": 140.8000,
            "speed": 100
        },
        {
            "drone_id": "DR003",
            "lat": 36.1000,
            "lon": 140.3000,
            "speed": 140
        }
    ]

# Create initial drone list
drones = create_initial_drones()

# Start timer
start_time = time.time()

# Distance calculation
def calculate_distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) * 111

while True:

    # Reset system every 15 minutes
    if time.time() - start_time > RESET_INTERVAL:

        print("Resetting system...")

        # Delete old telemetry data
        collection.delete_many({})

        # Reset drones
        drones = create_initial_drones()

        # Restart timer
        start_time = time.time()

        print("System reset completed")

    for drone in drones:

        # Move drone toward Tokyo
        drone["lat"] += (TOKYO_LAT - drone["lat"]) * 0.01
        drone["lon"] += (TOKYO_LON - drone["lon"]) * 0.01

        # Random speed variation
        drone["speed"] += random.uniform(-2, 2)

        # Prevent negative speed
        if drone["speed"] < 50:
            drone["speed"] = 50

        distance = calculate_distance(
            drone["lat"],
            drone["lon"],
            TOKYO_LAT,
            TOKYO_LON
        )

        # ETA calculation
        eta = (distance / drone["speed"]) * 60

        # Threat level logic
        threat = "Low"

        if distance < 20:
            threat = "Critical"
        elif distance < 50:
            threat = "High"
        elif distance < 100:
            threat = "Medium"

        # Create telemetry document
        document = {
            "drone_id": drone["drone_id"],
            "timestamp": datetime.utcnow(),
            "latitude": round(drone["lat"], 6),
            "longitude": round(drone["lon"], 6),
            "speed_kmh": round(drone["speed"], 2),
            "distance_to_tokyo_km": round(distance, 2),
            "eta_minutes": round(eta, 2),
            "threat_level": threat
        }

        # Insert into MongoDB
        collection.insert_one(document)

        # Print output
        print(document)

    # Wait 1 second before next update
    time.sleep(1)