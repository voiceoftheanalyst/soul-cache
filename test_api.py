import requests
import json
import subprocess
import logging
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def find_api_port():
    try:
        cmd = "lsof -i TCP:5000-6000 | grep LISTEN | grep python3"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            for line in result.stdout.splitlines():
                parts = line.split()
                for part in parts:
                    if ':' in part:
                        port = part.split(':')[-1]
                        try:
                            return int(port)
                        except ValueError:
                            continue
        
        logger.error("No Python API server found running")
        return None
        
    except Exception as e:
        logger.error(f"Error finding API port: {e}")
        return None

def test_endpoint(url, method='GET', data=None):
    try:
        logger.info(f"Testing {method} {url}")
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=5)
        else:
            response = requests.post(url, json=data, headers=headers, timeout=5)
        
        logger.debug(f"Response Status: {response.status_code}")
        logger.debug(f"Response Headers: {dict(response.headers)}")
        
        try:
            json_response = response.json()
            logger.debug(f"Response Body: {json.dumps(json_response, indent=2)}")
            return response.status_code, json_response
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON response: {response.text}")
            return response.status_code, None
            
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection refused to {url}")
        return None, None
    except Exception as e:
        logger.error(f"Error testing {url}: {e}")
        return None, None

def main():
    port = find_api_port()
    if not port:
        logger.error("Could not find API port. Is the API running?")
        sys.exit(1)
    
    base_url = f"http://localhost:{port}"
    logger.info(f"Testing API at {base_url}")
    
    # Test health check endpoint
    status, response = test_endpoint(f"{base_url}/")
    if status != 200:
        logger.error("Health check failed")
    
    # Test store_session endpoint
    test_data = {
        "text": "This is a test chat session",
        "title": "Test Session",
        "tags": ["test", "debug"]
    }
    
    status, response = test_endpoint(
        f"{base_url}/store_session",
        method='POST',
        data=test_data
    )
    
    if status != 200:
        logger.error("Store session test failed")

if __name__ == "__main__":
    main()
