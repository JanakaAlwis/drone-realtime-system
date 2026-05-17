from pymongo import MongoClient
from datetime import datetime, UTC
import random
import math
import os

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["drone_monitoring"]
collection = db["drone_telemetry1"]

# Tokyo coordinates
TOKYO_LAT = 35.6764
TOKYO_LON = 139.6500

# Initial drones
drones = [
    {"drone_id": "DR001"},
    {"drone_id": "DR002"},
    {"drone_id": "DR003"}
]

# Distance calculation
def calculate_distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) * 111

print("Simulation started")

# INSERT 10 RECORDS
for i in range(40):

    drone = random.choice(drones)

    latitude = round(random.uniform(35.5, 36.5), 6)
    longitude = round(random.uniform(139.5, 141.5), 6)

    speed = round(random.uniform(80, 180), 2)

    distance = calculate_distance(
        latitude,
        longitude,
        TOKYO_LAT,
        TOKYO_LON
    )

    eta = round((distance / speed) * 60, 2)

    threat = "Low"

    if distance < 20:
        threat = "Critical"
    elif distance < 50:
        threat = "High"
    elif distance < 100:
        threat = "Medium"

    document = {

        "drone_id": drone["drone_id"],
        "timestamp": datetime.now(UTC),

        "latitude": latitude,
        "longitude": longitude,

        "city_target": random.choice([
            "Tokyo",
            "Osaka",
            "Yokohama"
        ]),

        "speed_kmh": speed,
        "altitude_m": random.randint(100, 1200),

        "distance_to_tokyo_km": round(distance, 2),
        "eta_minutes": eta,

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

    collection.insert_one(document)

    print(f"Inserted record {i+1}")

print("Simulation completed")