import sys
import tempfile
import subprocess
import os
import json

def main():
    # Read JSON from stdin
    data = json.load(sys.stdin)
    code = data.get("code", "")
    user_input = data.get("input", "")

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
        # Run the code and measure resources
        result = subprocess.run(
            ["/usr/bin/time", "-f", "USED_TIME=%U;SYS_TIME=%S;ELAPSED=%E;MEM_KB=%M", "python3", code_filename],
            stdin=open(input_filename, "r"),
            capture_output=True,
            text=True,
            timeout=5
        )

        program_output = result.stdout.strip()
        resource_line = result.stderr.strip().splitlines()[-1]

        resources = {}
        for part in resource_line.split(";"):
            if "=" in part:
                key, val = part.split("=")
                resources[key] = val

        # Output program result + resource info as JSON
        output = {
            "output": program_output,
            "error": None if result.returncode == 0 else result.stderr.strip(),
            "exit_code": result.returncode,
            "resources": resources
        }

        print(json.dumps(output))

    except subprocess.TimeoutExpired:
        print(json.dumps({
            "output": "",
            "error": "Time Limit Exceeded",
            "exit_code": -1,
            "resources": {}
        }))

    finally:
        os.remove(code_filename)
        os.remove(input_filename)


if __name__ == "__main__":
    main()
