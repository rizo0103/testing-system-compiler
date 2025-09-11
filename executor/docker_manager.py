import os, subprocess, uuid, time, shutil

TEMP_DIR = os.path.join(os.path.dirname(__file__), 'temp')

def run_in_docker(code: str, input: str, expected_output: str, ext: str, time_limit: int, memory_limit: int, output_validator_code=None) -> dict:
    """
    Runs user code inside a Docker container
    Currently supports Python and C++
    """

    # Create temp folder for this run
    run_id = str(uuid.uuid4())[:8]
    run_path = os.path.join(TEMP_DIR, run_id)
    os.makedirs(run_path, exist_ok=True)

    # File mapping by language
    file_map = {
        "python": "solution.py",
        "cpp": "solution.cpp",
        "js": "solution.js"
    }

    if ext not in file_map:
        raise ValueError(f"Unsupported language extension: {ext}")

    code_filename = file_map[ext]
    input_filename = "input.txt"
    output_filename = "output.txt"

    # Write code, input and output into temp folder
    with open(os.path.join(run_path, code_filename), 'w') as f:
        f.write(code)
    with open(os.path.join(run_path, input_filename), 'w') as f:
        f.write(input)
    with open(os.path.join(run_path, output_filename), 'w') as f:
        f.write(expected_output)
    
    # Build docker run command
    image_map = {
        "python": "code-runner-python",
        "cpp": "code-runner-cpp",
        "js": "code-runner-javascript"
    }

    image = image_map.get(ext)
    if not image:
        raise ValueError(f"No Docker image found for extension: {ext}")
    
    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{run_path}:/app",
        image
    ]

    # Run inside Docker with timeout
    try:
        start_time = time.time()
        result = subprocess.run(
            docker_cmd, 
            capture_output=True,
            text=True,
            timeout=5,
        )
        end_time = time.time()

        exec_time = round(end_time - start_time, 3)

        response = {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exec_time": exec_time,
            "memory": None, # Memory usage tracking can be added with more complex setups
        }
    except subprocess.TimeoutExpired:
        response = {
            "error": "Time limit exceeded",
            "stdout": "",
            "stderr": "",
            "exit_code": None,
            "memory": None,
            "time": None
        }
    
    finally:
        # Cleanup temp folder
        shutil.rmtree(run_path, ignore_errors=True)
    
    return response
