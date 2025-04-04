# tests/test_api_endpoints.py
import requests
import json
import time
import os

# API base URL
API_BASE = "http://localhost:8000"

def test_api_endpoints():
    """
    Test all API endpoints of the AI Psychologist
    """
    print("Testing API endpoints...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"Server status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Server not running: {str(e)}")
        return
    
    # Test 2: Create a user
    print("\nCreating test user...")
    user_data = {
        "username": f"api_test_user_{int(time.time())}",
        "language": "tr",
        "preferred_therapy_approach": "cbt"
    }
    
    response = requests.post(f"{API_BASE}/api/v1/users/", json=user_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        user_info = response.json()
        user_id = user_info["id"]
        print(f"Created user ID: {user_id}")
        
        # Test 3: Create a session
        print("\nCreating therapy session...")
        session_data = {
            "user_id": user_id,
            "therapy_approach": "cbt",
            "title": "API Test Session"
        }
        
        response = requests.post(f"{API_BASE}/api/v1/sessions/", json=session_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            session_info = response.json()
            session_id = session_info["id"]
            print(f"Created session ID: {session_id}")
            
            # Test 4: Send a message
            print("\nSending test message...")
            message_data = {
                "session_id": session_id,
                "message": "Merhaba, bugün biraz endişeliyim.",
                "is_voice": False
            }
            
            response = requests.post(f"{API_BASE}/api/v1/chat/send", json=message_data)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                chat_response = response.json()
                print(f"AI Response: {chat_response['response'][:200]}...")
                print(f"Crisis detected: {chat_response['crisis_detected']}")
                
                # Test 5: End the session
                print("\nEnding session...")
                end_data = {
                    "ended_at": time.strftime("%Y-%m-%dT%H:%M:%S")
                }
                
                response = requests.put(f"{API_BASE}/api/v1/sessions/{session_id}", json=end_data)
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print("Session ended successfully")
    
    print("\nAPI testing completed!")

if __name__ == "__main__":
    test_api_endpoints()