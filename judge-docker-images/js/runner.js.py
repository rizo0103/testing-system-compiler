import sys, tempfile, subprocess, os, json, platform

def main():
    data = json.load(sys.stdin)
    code = data.get("code", "")
    user_input = data.get("input", "")
    validator_code = data.get("validator_code", "")
    expected = data.get("expected", "")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".js") as code_file:
        code_file.write(code.encode())
        code_file.flush()
        code_filename = code_file.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as input_file:
        input_file.write(user_input.encode())
        input_file.flush()
        input_filename = input_file.name

    try:
        if platform.system() == "Linux":
            cmd = ["/usr/bin/time", "-f", "USED_TIME=%U;SYS_TIME=%S;ELAPSED=%E;MEM_KB=%M", "node", code_filename]
        else:
            cmd = ["node", code_filename]

        with open(input_filename, "r") as f_in:
            result = subprocess.run(
                cmd,
                stdin=f_in,
                capture_output=True,
                text=True,
                timeout=5
            )

        program_output = result.stdout.strip()
        stderr_lines = result.stderr.strip().splitlines()

        resources = {}
        if platform.system() == "Linux" and stderr_lines:
            resource_line = stderr_lines[-1]
            if "USED_TIME" in resource_line:
                for part in resource_line.split(";"):
                    if "=" in part:
                        key, val = part.split("=")
                        resources[key] = val
                stderr_lines = stderr_lines[:-1]

        if result.returncode != 0:
            print(json.dumps({
                "output": program_output,
                "error": "\n".join(stderr_lines) if stderr_lines else None,
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
            print(json.dumps({
                "output": program_output,
                "error": "\n".join(stderr_lines) if stderr_lines else None,
                "exit_code": result.returncode,
                "resources": resources
            }))

    except subprocess.TimeoutExpired:
        print(json.dumps({"output": "", "error": "Time Limit Exceeded", "exit_code": -1, "resources": {}}))

    finally:
        try:
            os.remove(code_filename)
        except: pass
        try:
            os.remove(input_filename)
        except: pass

if __name__ == "__main__":
    main()
