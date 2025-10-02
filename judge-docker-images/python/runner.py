import sys
import tempfile
import subprocess
import os
import json

def main():
    # Read JSON from stdin
    data = json.load(sys.stdin)
    code = data.get("code", "")
    validator_code = data.get("validator_code", "")
    user_input = data.get("input", "")
    expected = data.get("expected", "")

    # Save code to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as code_file:
        code_file.write(code.encode())
        code_file.flush()
        code_filename = code_file.name

    # Save input to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as input_file:
        input_file.write(user_input.encode())
        input_file.flush()
        input_filename = input_file.name

    try:
        # Run the user's code
        result = subprocess.run(
            ["/usr/bin/time", "-f", "USED_TIME=%U;SYS_TIME=%S;ELAPSED=%E;MEM_KB=%M", "python3", code_filename],
            stdin=open(input_filename, "r"),
            capture_output=True,
            text=True,
            timeout=5
        )

        program_output = result.stdout.strip()
        resource_line = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else ""

        resources = {}
        if "USED_TIME" in resource_line:
            for part in resource_line.split(";"):
                if "=" in part:
                    key, val = part.split("=")
                    resources[key] = val
        
        if result.returncode != 0:
            print(json.dumps({
                "output": program_output,
                "error": result.stderr.strip(),
                "exit_code": result.returncode,
                "resources": resources
            }))
            return

        if validator_code:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".cpp") as validator_file:
                validator_file.write(validator_code.encode())
                validator_file.flush()
                validator_filename = validator_file.name
            
            compile_result = subprocess.run(["g++", validator_filename, "-o", "validator"], capture_output=True, text=True)

            if compile_result.returncode != 0:
                print(json.dumps({"output": "", "error": f"Validator compilation failed: {compile_result.stderr}", "exit_code": -1, "resources": resources}))
                return

            # Validate user's output
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as user_output_file:
                user_output_file.write(program_output.encode())
                user_output_filename = user_output_file.name
            user_validator_result = subprocess.run(["./validator", user_output_filename], capture_output=True, text=True)
            user_verdict = user_validator_result.stdout.strip().lower()

            # Validate expected output
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as expected_output_file:
                expected_output_file.write(expected.encode())
                expected_output_filename = expected_output_file.name
            expected_validator_result = subprocess.run(["./validator", expected_output_filename], capture_output=True, text=True)
            expected_verdict = expected_validator_result.stdout.strip().lower()

            verdict = "Wrong Answer"
            if user_verdict == "true" and expected_verdict == "true":
                verdict = "Accepted"

            print(json.dumps({"output": program_output, "verdict": verdict, "error": None, "exit_code": result.returncode, "resources": resources}))

            os.remove(validator_filename)
            os.remove("validator")
            os.remove(user_output_filename)
            os.remove(expected_output_filename)

        else:
            print(json.dumps({"output": program_output, "error": None if result.returncode == 0 else result.stderr.strip(), "exit_code": result.returncode, "resources": resources}))

    except subprocess.TimeoutExpired:
        print(json.dumps({"output": "", "error": "Time Limit Exceeded", "exit_code": -1, "resources": {}}))

    finally:
        os.remove(code_filename)
        os.remove(input_filename)

if __name__ == "__main__":
    main()