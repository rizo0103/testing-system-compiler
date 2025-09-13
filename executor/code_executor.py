import subprocess

def execute_python_code(data):
    try:
        # Run docker container and pass code via stdin
        result = subprocess.run(
            ["docker", "run", "-i", "--rm", "code-runner-python"],
            input=data,
            text=True,
            capture_output=True,
            timeout=10  # safety timeout in seconds
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exitCode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"error": "Time Limit Exceeded", "exitCode": -1}
    except Exception as e:
        return {"error": str(e), "exitCode": -1}

def execute_cpp_code(code):
    try:
        # Run docker container and pass code via stdin
        result = subprocess.run(
            ["docker", "run", "-i", "--rm", "code-runner-cpp"],
            input=code,
            text=True,
            capture_output=True,
            timeout=10  # safety timeout in seconds
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exitCode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"error": "Time Limit Exceeded", "exitCode": -1}
    except Exception as e:
        return {"error": str(e), "exitCode": -1}

def execute_js_code(code):
    try:
        # Run docker container and pass code via stdin
        result = subprocess.run(
            ["docker", "run", "-i", "--rm", "code-runner-js"],
            input=code,
            text=True,
            capture_output=True,
            timeout=10  # safety timeout in seconds
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exitCode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"error": "Time Limit Exceeded", "exitCode": -1}
    except Exception as e:
        return {"error": str(e), "exitCode": -1}
