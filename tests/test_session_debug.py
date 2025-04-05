import requests
import time

def test_session_creation():
    """Test session creation with detailed error output"""
    BASE_URL = "http://localhost:8000"
    
    # Create test user
    user_data = {
        "username": f"debug_user_{int(time.time())}",
        "language": "tr",
        "preferred_therapy_approach": "cbt"
    }
    
    user_response = requests.post(f"{BASE_URL}/api/v1/users/", json=user_data)
    print(f"User creation status: {user_response.status_code}")
    
    if user_response.status_code == 200:
        user_info = user_response.json()
        user_id = user_info["id"]
        print(f"Created user ID: {user_id}")
        
        # Try to create session with detailed error output
        session_data = {
            "user_id": user_id,
            "therapy_approach": "cbt",
            "title": "Debug Test Session"
        }
        
        print(f"\nSending session data: {session_data}")
        session_response = requests.post(f"{BASE_URL}/api/v1/sessions/", json=session_data)
        print(f"Session creation status: {session_response.status_code}")
        
        try:
            response_json = session_response.json()
            print(f"\nDetailed response: {response_json}")
        except Exception as e:
            print(f"Error parsing response: {e}")

if __name__ == "__main__":
    test_session_creation()