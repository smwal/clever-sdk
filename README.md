# Clever API Python Module
This repository contains a Python module for interacting with the Clever Data API. It allows for seamless integration with Clever’s data systems, enabling operations like retrieving user, classroom, and school data.

## Installation

Clone the repository:

```
git clone https://github.com/yourusername/clever-api-python.git
```

## Install dependencies:
```
pip install -r requirements.txt
```

## Usage

### Set up your API credentials by creating a .env file with the following variables:

```
CLEVER_API_TOKEN = ""
```
Note: This token must be a district-app token. Any other token, such as an SSO Bearer Token, will not work for the endpoints queried in this SDK.

### Testing the SDK
If you would like to test the SDK, you can run the following command in the venv:

```
python clever-sdk.py
```

This will run the #Example Usage section of the script to pull some data associated with your District-App Token (CLEVER_API_TOKEN in your .env file).


### Import the module and start using it:

```
from clever_api import CleverAPI
```

### Initialize the API client

```
api = CleverAPI()
```
### Example: Get a list of sections

```
sections = api.get_sections()
print(students)
```
