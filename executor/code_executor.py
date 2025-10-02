import subprocess, json, requests
# from config import PYTHON_RUNNER_URL, CPP_RUNNER_URL

PYTHON_RUNNER_URL = "https://code-runner-python-358107326233.us-central1.run.app/run"
CPP_RUNNER_URL = "https://code-runner-cpp-358107326233.us-central1.run.app/run"
JS_RUNNER_URL = "https://code-runner-js-358107326233.us-central1.run.app/run"

def execute_python_code(payload_json):
    """
    payload_json: JSON string with keys:
        - code: str (user's code)
        - input: str (test case input)
        - validator_code: str (code for multiple answers, optional)
    Returns dict with:
        - output: str
        - error: str (if any)
        - exit_code: int
        - resources: {time, memory} (optional)
    """

    print("Payload json in code executor py ", payload_json)

    try:
        headers = {
            "Content-Type": "application/json",
        }
        response = requests.post(
            PYTHON_RUNNER_URL,
            headers=headers,
            json=json.loads(payload_json),  # safer with requests
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {
                "output": "",
                "error": f"Runner returned {response.status_code}: {response.text}",
                "exit_code": -1,
                "resources": {}
            }

    except requests.exceptions.Timeout:
        return {
            "output": "",
            "error": "Time Limit Exceeded",
            "exit_code": -1,
            "resources": {}
        }

    except Exception as e:
        return {
            "output": "",
            "error": f"Execution Error: {str(e)}",
            "exit_code": -1,
            "resources": {}
        }

def execute_cpp_code(payload_json: str) -> dict:
    """
    payload_json: JSON string with keys:
        - code: str (C++ source code)
        - input: str (stdin input for the program)
    Returns dict with:
        - output: str
        - error: str (if any)
        - exit_code: int
        - resources: {USED_TIME, SYS_TIME, ELAPSED, MEM_KB}
    """
    try:
        headers = {"Content-Type": "application/json"}

        response = requests.post(
            CPP_RUNNER_URL,
            headers=headers,
            json=json.loads(payload_json),
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        
        else:
            return {
                "output": "",
                "error": f"Runner returned {response.status_code}: {response.text}",
                "exit_code": -1,
                "resources": {}
            }

    except requests.exceptions.Timeout:
        return {
            "output": "",
            "error": "Time Limit Exceeded",
            "exit_code": -1,
            "resources": {}
        }

    except Exception as e:
        return {
            "output": "",
            "error": f"Execution Error: {str(e)}",
            "exit_code": -1,
            "resources": {}
        }

def execute_js_code(payload_json):
    """
    payload_json: JSON string with keys:
        - code: str
        - input: str
    Returns dict with:
        - output: str
        - error: str (if any)
        - exit_code: int
        - resources: {time, memory} (optional)
    """
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            JS_RUNNER_URL,
            headers=headers,
            json=json.loads(payload_json),
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {
                "output": "",
                "error": f"Runner returned {response.status_code}: {response.text}",
                "exit_code": -1,
                "resources": {}
            }

    except requests.exceptions.Timeout:
        return {
            "output": "",
            "error": "Time Limit Exceeded",
            "exit_code": -1,
            "resources": {}
        }

    except Exception as e:
        return {
            "output": "",
            "error": f"Execution Error: {str(e)}",
            "exit_code": -1,
            "resources": {}
        }