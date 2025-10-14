# Online Code Judging System

This project is a web-based online judge that allows users to submit code in Python, C++, and JavaScript and have it evaluated against a set of test cases. The system is designed with a microservices-based architecture, where each programming language has its own dedicated execution environment running inside a Docker container.

## Features

- **Multi-language Support:** Execute and test code written in Python, C++, and JavaScript.
- **Flexible Testing:** Run code with custom input or submit it for evaluation against predefined test cases.
- **Resource Limiting:** Set time and memory limits for code execution to handle inefficient or malicious code.
- **Detailed Results:** Get detailed results for each test case, including the verdict (Accepted, Wrong Answer, etc.), input, expected output, and user's output.
- **RESTful API:** A simple and clean API for submitting code and retrieving results.

## API Endpoints

### `POST /run/<lang>`

Execute a piece of code with a given input.

-   **URL Params:** `lang` can be `py`, `cpp`, or `js`.
-   **Request Body:**
    ```json
    {
        "code": "print(input())",
        "input": "Hello, World!"
    }
    ```
-   **Success Response (200):**
    ```json
    {
        "output": "Hello, World!\n",
        "error": "",
        "exit_code": 0,
        "resources": { ... }
    }
    ```
-   **Error Response (400, 500):**
    ```json
    {
        "error": "Error message"
    }
    ```

### `POST /task-submission`

Submit code to be judged against a set of test cases.

-   **Request Body:**
    ```json
    {
        "code": "n = int(input())\nprint(n * 2)",
        "lang": "py",
        "test_cases": [
            {"input": "2", "expected": "4"},
            {"input": "5", "expected": "10"}
        ],
        "time_limit": 1,
        "memory_limit": 128
    }
    ```
-   **Success Response (200):**
    ```json
    {
        "overall": "Accepted",
        "details": [
            {
                "test_case": 1,
                "input": "2",
                "expected": "4",
                "user_output": "4",
                "status": "Accepted",
                "resources": { ... }
            },
            {
                "test_case": 2,
                "input": "5",
                "expected": "10",
                "user_output": "10",
                "status": "Accepted",
                "resources": { ... }
            }
        ]
    }
    ```

## Project Structure

```
.
├── app.py                  # Main Flask application (API gateway)
├── executor/
│   ├── __init__.py
│   ├── code_executor.py    # Logic to call the language-specific runner services
├── judge-docker-images/
│   ├── python/
|   |   ├── app.py # Flask application for python code running
│   │   ├── Dockerfile
│   │   ├── requirements.txt # Requirements for Flask app
│   │   └── runner.py # Code runner for python
│   ├── cpp/
|   |   ├── app.py # Flask application for cpp code running
│   │   ├── Dockerfile
│   │   ├── requirements.txt # Requirements for Flask app
│   │   └── runner.cpp.py # Code runner for cpp
│   ├── js/
|   |   ├── app.py # Flask application for js code running
│   │   ├── Dockerfile
│   │   ├── requirements.txt # Requirements for Flask app
│   │   └── runner.py # Code runner for js
├── requirements.txt        # Python dependencies for the main app
└── README.md
```
