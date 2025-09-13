import subprocess
import json

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

def execute_cpp_code(data):
    try:
        # Run docker container and pass code via stdin
        result = subprocess.run(
            ["docker", "run", "-i", "--rm", "code-runner-cpp"],
            input=data,
            text=True,
            capture_output=True,
            timeout=10  # safety timeout in seconds
        )

        try:
            # The runner script returns a JSON string
            output_data = json.loads(result.stdout)
            program_stdout = output_data.get("output", "")
            resource_usage = output_data.get("usage", None)
        except (json.JSONDecodeError, AttributeError):
            # If output is not JSON, treat it as raw output
            program_stdout = result.stdout
            resource_usage = None

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
