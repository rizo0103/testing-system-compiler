import requests
import json


url = "http://localhost:5000/task-submission" 
data = {
    "code": "while True: pass",  # Бесконечный цикл
    "lang": "py",
    "test_cases": [
        {"input": "", "expected": ""}
    ],
    "time_limit": 1  
}

response = requests.post(url, json=data)
print("Таймаут:")
print(json.dumps(response.json(), indent=2))