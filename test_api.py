import requests
import json

def test_api(port=3000):
    base_url = f"http://127.0.0.1:{port}"
    
    # Test health check
    print(f"\nTesting health check at {base_url}")
    try:
        response = requests.get(f"{base_url}/")
        print(f"Health check response: {response.json()}")
    except Exception as e:
        print(f"Health check error: {e}")
        return
    
    # Test store_session
    print("\nTesting store_session endpoint")
    test_data = {
        "text": "Test message",
        "title": "Test",
        "tags": ["test"]
    }
    
    try:
        response = requests.post(
            f"{base_url}/store_session",
            json=test_data
        )
        print(f"Store session response: {response.json()}")
    except Exception as e:
        print(f"Store session error: {e}")

if __name__ == "__main__":
    test_api()
