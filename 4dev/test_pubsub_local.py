#!/usr/bin/env python3
"""
Local PubSub testing utility for NASA Hackathon project.
This script helps test PubSub message publishing and consumption locally.
"""

import json
import sys
import os
import time
from google.cloud import pubsub_v1
from google.api_core.client_options import ClientOptions

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import project-specific modules
from functions.lib.gcloud.pub_sub import TOPIC_ID_PREDICTION, PROJECT_ID, PublishPredictionPayload

# Configure for local emulator
os.environ["PUBSUB_EMULATOR_HOST"] = "localhost:8085"

def publish_test_message():
    """Publish a test message to the local PubSub emulator"""

    print(f"\n🔄 Publishing test message to topic: {TOPIC_ID_PREDICTION}")

    # Create sample payload
    payload = PublishPredictionPayload(
        id_user="test_user_123",
        latitude=37.7749,
        longitude=-122.4194,
        crop_type="corn",
        start_month="march"
    )

    # Create publisher client for local emulator
    publisher = pubsub_v1.PublisherClient(
        client_options=ClientOptions(api_endpoint="localhost:8085")
    )

    # Format topic path for emulator
    topic_path = f"projects/{PROJECT_ID}/topics/{TOPIC_ID_PREDICTION}"

    # Publish message
    try:
        future = publisher.publish(
            topic_path,
            json.dumps(payload.model_dump()).encode("utf-8")
        )
        message_id = future.result()
        print(f"✅ Message published with ID: {message_id}")
        print(f"Message content: {json.dumps(payload.model_dump(), indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Error publishing message: {e}")
        return False

def check_emulator_running():
    """Verify if the PubSub emulator is running"""
    import socket

    host = "localhost"
    port = 8085

    try:
        socket.create_connection((host, port), timeout=3)
        print("✅ PubSub emulator is running at localhost:8085")
        return True
    except (socket.timeout, ConnectionRefusedError):
        print("❌ PubSub emulator is not running!")
        print("Start it with: firebase emulators:start")
        return False

def main():
    print("\n🚀 NASA Hackathon - Local PubSub Testing Utility 🚀")

    if not check_emulator_running():
        return

    # Publish test message
    if publish_test_message():
        print("\n📝 Check the Firebase emulator logs to see if your function was triggered!")
        print("Look for log messages from your start_prediction_worker function\n")
        print("Your enhanced logging should show details about the message processing.")

if __name__ == "__main__":
    main()
