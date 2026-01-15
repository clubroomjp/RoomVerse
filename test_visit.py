import requests
import json
import sys

def test_visit():
    base_url = "http://localhost:22022"
    
    # 1. Test Card
    print(f"--- Testing /card ---")
    try:
        resp = requests.get(f"{base_url}/card")
        resp.raise_for_status()
        print(resp.json())
    except Exception as e:
        print(f"Card Error: {e}")

    # 2. Test Visit
    print(f"\n--- Testing /visit ---")
    payload = {
        "visitor_id": "test-visitor-uuid-1234",
        "visitor_name": "Traveler",
        "message": "Hello! I am just passing by using the new database.",
        "callback_url": "https://fake-visitor.ngrok.io",
        "context": []
    }
    
    headers = {
        "X-RoomVerse-Key": "secret-verse-key"
    }

    try:
        response = requests.post(f"{base_url}/visit", json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        print(f"Response: {data['response']}")
    except Exception as e:
        print(f"Visit Error: {e}")
        return False
        
    # 3. Test Chat
    print(f"\n--- Testing /chat ---")
    chat_payload = {
        "visitor_id": "test-visitor-uuid-1234",
        "message": "Nice to meet you! Can we talk more?"
    }
    
    try:
        response = requests.post(f"{base_url}/chat", json=chat_payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        print(f"Session: {data['session_id']}")
        print(f"Response: {data['response']}")
    except Exception as e:
        print(f"Chat Error: {e}")
        return False

    return True

if __name__ == "__main__":
    if test_visit():
        sys.exit(0)
    else:
        sys.exit(1)
