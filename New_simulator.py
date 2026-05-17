from pymongo import MongoClient
from datetime import datetime, UTC
import random
import math
import os

# MongoDB Atlas connection
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["drone_monitoring"]
collection = db["drone_telemetry1"]

# Tokyo coordinates
TOKYO_LAT = 35.6764
TOKYO_LON = 139.6500

# Initial drones
drones = [
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

# Distance calculation
def calculate_distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) * 111

print("Drone simulation started...")

# Generate ONE telemetry batch
for drone in drones:

    # Move drone toward Tokyo
    drone["lat"] += random.uniform(-0.05, 0.05)
    drone["lon"] += random.uniform(-0.05, 0.05)

    # Random speed variation
    drone["speed"] += random.uniform(-5, 5)

    # Prevent negative speed
    if drone["speed"] < 50:
        drone["speed"] = 50

    distance = calculate_distance(
        drone["lat"],
        drone["lon"],
        TOKYO_LAT,
        TOKYO_LON
    )

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
        "timestamp": datetime.now(UTC),

        # Location
        "latitude": round(drone["lat"], 6),
        "longitude": round(drone["lon"], 6),
        "city_target": random.choice([
            "Tokyo",
            "Osaka",
            "Yokohama"
        ]),

        # Movement
        "speed_kmh": round(drone["speed"], 2),
        "altitude_m": random.randint(100, 1200),
        "distance_to_tokyo_km": round(distance, 2),
        "eta_minutes": round(eta, 2),

        # Threat
        "threat_level": threat,
        "threat_score": random.randint(1, 100),
        "payload_risk": random.randint(1, 10),
        "restricted_zone": random.choice([True, False]),

        # Drone intelligence
        "drone_type": random.choice([
            "Commercial",
            "Unknown",
            "Military",
            "Hobby",
            "Autonomous"
        ]),

        # Technical telemetry
        "signal_strength": random.randint(60, 100),
        "battery_level": random.randint(20, 100),

        # Security operations
        "detection_confidence": round(random.uniform(70, 99), 2),
        "response_time_sec": random.randint(10, 300),

        "intercept_status": random.choice([
            "Monitoring",
            "Tracking",
            "Intercepted",
            "Escaped"
        ])
    }

    # Insert into MongoDB
    collection.insert_one(document)

    print("Inserted:", document["drone_id"])

print("Simulation completed.")