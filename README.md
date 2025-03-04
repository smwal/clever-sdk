# Clever API Python Module
This repository contains a Python module for interacting with the Clever API. It allows for seamless integration with Clever’s data systems, enabling operations like retrieving student, teacher, and school data.

## Features

Access Clever API: Easily connect to and retrieve data from the Clever API.
Authentication: Handles OAuth 2.0 authentication for secure API access.
Data Retrieval: Supports fetching data related to students, teachers, classes, and schools.

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
