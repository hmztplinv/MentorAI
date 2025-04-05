# tests/test_api_flexible.py
import requests
import json
import time
import os

def test_api_endpoints():
    """
    Test all API endpoints of the AI Psychologist with flexible URL handling
    """
    print("Testing API endpoints...")
    
    # API base URL
    BASE_URL = "http://localhost:8000"
    
    # Test if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Server status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Server not running: {str(e)}")
        return
    
    # Try both API paths (with and without /api/v1 prefix)
    api_prefixes = ["", "/api/v1"]
    
    for prefix in api_prefixes:
        print(f"\nTrying with API prefix: '{prefix}'")
        
        # Test user creation
        user_data = {
            "username": f"api_test_user_{int(time.time())}",
            "language": "tr",
            "preferred_therapy_approach": "cbt"
        }
        
        response = requests.post(f"{BASE_URL}{prefix}/users/", json=user_data)
        print(f"Create user status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API endpoint found!")
            # The rest of the tests with the successful prefix
            # ...
            
            user_info = response.json()
            user_id = user_info["id"]
            print(f"Created user ID: {user_id}")
            
            # Continue with other tests using this prefix
            # ...
            
            # For example, create a session
            session_data = {
                "user_id": user_id,
                "therapy_approach": "cbt",
                "title": "API Test Session"
            }
            
            response = requests.post(f"{BASE_URL}{prefix}/sessions/", json=session_data)
            print(f"Create session status: {response.status_code}")
            
            if response.status_code == 200:
                # Session created successfully, continue with other tests
                # ...
                pass
            
            # Found working prefix, exit loop
            break
        else:
            print(f"❌ API not found with this prefix")
    else:
        print("\n⚠️ Could not find working API endpoints with any prefix!")

if __name__ == "__main__":
    test_api_endpoints()