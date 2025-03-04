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

    def get_all(self, limit=1, starting_after=None, role=None):
        params = {"limit": limit}
        if starting_after:
            params["starting_after"] = starting_after
        if role:
            params["role"] = role  # Include 'role' as an optional query parameter
        return self.client.request("GET", f"/{self.resource}", params=params)

# Function to save responses as JSON files in output folder
def save_response_to_file(data, filename, folder="output"):
    """Save API response data to a formatted JSON file in a specified folder."""
    try:
        # Check if the folder exists, create it if it doesn't
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        # Check if 'data' field is empty or missing
        if not data or "data" not in data or not data["data"]:
            logging.warning(f"No data returned for {filename}. Skipping file save.")
            return
        
        # Define the full file path
        filepath = os.path.join(folder, filename)
        
        # Save the data to the file
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)  # Pretty-print JSON
        logging.info(f"Response saved to {filepath}")
    
    except Exception as e:
        logging.error(f"Error saving response to file: {e}")

# Example usage
if __name__ == "__main__":
    token = os.getenv("CLEVER_API_TOKEN")
    
    # Ask for role input or specify "n" for a single user
    user_role = input("Enter user role (student, teacher, staff, or district_admin) or 'n' for a single user: ").strip().lower()

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

    # Specify the folder where the JSON files should be saved
    output_folder = "output_data"  # Change this to any folder name you prefer

    for resource_name, api_obj in api_objects.items():
        try:
            # Fetch users with the role if provided, or fetch a single user if "n" is entered
            if resource_name == "users":
                if user_role == "n":
                    # If the user input is "n", fetch a single user (without passing the role parameter)
                    data = api_obj.get_all(limit=1)
                else:
                    # Otherwise, fetch users with the specified role
                    data = api_obj.get_all(limit=1, role=user_role)
            else:
                # For other resources, no role filter is applied
                data = api_obj.get_all(limit=1)
            
            # Save the response to the specified folder
            save_response_to_file(data, f"{resource_name}.json", folder=output_folder)
        except Exception as e:
            logging.error(f"Failed to fetch {resource_name}: {e}")