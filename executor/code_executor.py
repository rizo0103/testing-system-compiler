import subprocess, json, requests
# from config import PYTHON_RUNNER_URL, CPP_RUNNER_URL

PYTHON_RUNNER_URL = "https://code-runner-python-358107326233.us-central1.run.app/run"
CPP_RUNNER_URL = "https://code-runner-cpp-358107326233.us-central1.run.app/run"

def execute_python_code(payload_json):
    """
    payload_json: JSON string with keys:
        - code: str (user's code)
        - input: str (test case input)
    Returns dict with:
        - output: str
        - error: str (if any)
        - exit_code: int
        - resources: {time, memory} (optional)
    """
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

def execute_js_code(data):
    try:
        # Run docker container and pass code via stdin
        result = subprocess.run(
            ["docker", "run", "-i", "--rm", "code-runner-javascript"],
            input=data,
            text=True,
            capture_output=True,
            timeout=10  # safety timeout in seconds
        )
        
        output_lines = result.stdout.strip().splitlines()
        program_stdout = ""
        resource_usage = None

        if output_lines:
            try:
                # Last line is expected to be resource usage JSON
                resource_usage = json.loads(output_lines[-1])
                program_stdout = "\n".join(output_lines[:-1])
            except (json.JSONDecodeError, IndexError):
                # If last line is not valid JSON, treat all output as stdout
                program_stdout = result.stdout

        return {
            "stdout": program_stdout,
            "stderr": result.stderr,
            "exitCode": result.returncode,
            "resources": resource_usage
        }
    except subprocess.TimeoutExpired:
        return {"error": "Time Limit Exceeded", "exitCode": -1}
    except Exception as e:
        return {"error": str(e), "exitCode": -1}
