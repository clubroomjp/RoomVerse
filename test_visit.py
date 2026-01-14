import requests
import json
import sys

def test_visit():
    url = "http://localhost:8001/visit"
    payload = {
        "visitor_id": "test-visitor-uuid-1234",
        "visitor_name": "Traveler",
        "message": "Hello! I am just passing by. What is this place?",
        "callback_url": "https://fake-visitor.ngrok.io",
        "context": []
    }
    
    headers = {
        "X-RoomVerse-Key": "secret-verse-key"
    }

    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        print("\n--- Response Received ---")
        print(f"Host: {data['host_name']}")
        print(f"Response: {data['response']}")
        print("-------------------------")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if test_visit():
        sys.exit(0)
    else:
        sys.exit(1)
