import json
import random
import time
import uuid
import requests
from app.core.config import load_config

def load_peers(path="peers.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def main():
    config = load_config()
    peers = load_peers()
    
    if not peers:
        print("No peers found in peers.json")
        return

    # Randomly select a peer
    target = random.choice(peers)
    target_url = target.get("url")
    if not target_url:
        print(f"Invalid peer entry: {target}")
        return

    # Prepare Visit Payload
    # Simple greeting selection
    greetings = [
        "Hello! I am exploring the network.",
        "Greetings! How is your day?",
        "Knock knock! Anyone home?",
        "I sensed another presence here.",
        "Just passing through, thought I'd say hi."
    ]
    
    payload = {
        "visitor_id": config.instance_id,
        "visitor_name": config.character.name,
        "message": random.choice(greetings),
        "callback_url": config.ngrok.authtoken if False else None, # TODO: We need a way to get our current public URL here
        "context": []
    }
    
    # Using my own API key if I have one configured for outgoing? 
    # For now, peers might have different keys or be open. Assuming open or shared key.
    headers = {}
    if config.security and config.security.api_key:
         headers["X-RoomVerse-Key"] = config.security.api_key

    print(f"Visiting {target['name']} at {target_url}...")
    
    try:
        resp = requests.post(f"{target_url}/visit", json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        print(f"Success! Host {data.get('host_name')} responded:")
        print(f"> {data.get('response')}")
    except Exception as e:
        print(f"Failed to visit {target_url}: {e}")

if __name__ == "__main__":
    main()
