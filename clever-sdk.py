import os
import time
import requests
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CleverAPIClient:
    BASE_URL = "https://api.clever.com/v3.0"
    RATE_LIMIT = 10  # Max requests per window
    RATE_LIMIT_WINDOW = 60  # Time window in seconds

    def __init__(self, token: str):
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        self.request_count = 0
        self.start_time = time.time()
    
    def enforce_rate_limit(self):
        elapsed_time = time.time() - self.start_time
        if self.request_count >= self.RATE_LIMIT:
            wait_time = max(0, self.RATE_LIMIT_WINDOW - elapsed_time)
            if wait_time > 0:
                logging.warning(f"Rate limit reached. Sleeping for {wait_time:.2f}s...")
                time.sleep(wait_time)
            self.start_time = time.time()
            self.request_count = 0
    
    def request(self, method: str, endpoint: str, params=None, cleverId=None):
        self.enforce_rate_limit()
        url = f"{self.BASE_URL}{endpoint}"
        if cleverId:
            url = f"{url}/{cleverId}"
        
        try:
            response = self.session.request(method, url, params=params)
            response.raise_for_status()
            self.request_count += 1
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {e}")
            return None

class CleverResource:
    def __init__(self, client: CleverAPIClient, resource: str):
        self.client = client
        self.resource = resource

    def get_all(self, limit=1, starting_after=None):
        params = {"limit": limit}
        if starting_after:
            params["starting_after"] = starting_after
        return self.client.request("GET", f"/{self.resource}", params=params)

    def get_by_id(self, cleverId: str):
        if not cleverId:
            raise ValueError("Clever object ID must be provided to fetch by ID")
        return self.client.request("GET", f"/{self.resource}", cleverId=cleverId)

# Specific Clever API resources
class Districts(CleverResource):
    def __init__(self, client: CleverAPIClient):
        super().__init__(client, "districts")

class Schools(CleverResource):
    def __init__(self, client: CleverAPIClient):
        super().__init__(client, "schools")

class Courses(CleverResource):
    def __init__(self, client: CleverAPIClient):
        super().__init__(client, "courses")

class Terms(CleverResource):
    def __init__(self, client: CleverAPIClient):
        super().__init__(client, "terms")

class Sections(CleverResource):
    def __init__(self, client: CleverAPIClient):
        super().__init__(client, "sections")

class Users(CleverResource):
    def __init__(self, client: CleverAPIClient):
        super().__init__(client, "users")

# Function to save responses to JSON files
def save_response_to_file(data, filename):
    """Save API response data to a formatted JSON file only if it contains data."""
    try:
        if not data or "data" not in data or not data["data"]:  # Check if 'data' field is empty or missing
            logging.warning(f"No data returned for {filename}. Skipping file save.")
            return
        
        filepath = os.path.join(os.getcwd(), filename) # Save in the current directory
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)  # Make the json file readable
        logging.info(f"Response saved to {filename}")
    
    except Exception as e:
        logging.error(f"Error saving response to file: {e}")

# Example usage
if __name__ == "__main__":
    token = os.getenv("CLEVER_API_TOKEN")
    if not token:
        logging.error("CLEVER_API_TOKEN is not set.")
        exit(1)
    
    client = CleverAPIClient(token)
    api_objects = {
        "districts": Districts(client),
        "schools": Schools(client),
        "sections": Sections(client),
        "courses": Courses(client),
        "terms": Terms(client),
        "users": Users(client),
    }

    for resource_name, api_obj in api_objects.items():
        try:
            data = api_obj.get_all(limit=1)
            save_response_to_file(data, f"{resource_name}.json")
        except Exception as e:
            logging.error(f"Failed to fetch {resource_name}: {e}")