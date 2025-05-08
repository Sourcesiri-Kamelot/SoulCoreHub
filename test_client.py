import requests
import json

data = {
    "jsonrpc": "2.0",
    "method": "build_app",
    "params": {
        "prompt": "Create a Django blog with user comments and tags"
    },
    "id": 1
}

response = requests.post("http://localhost:8000", json=data)
print(response.json())
