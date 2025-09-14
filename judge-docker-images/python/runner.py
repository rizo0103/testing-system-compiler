import sys, tempfile, subprocess, os, json

def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: runner.py <code> <input>"}))
        return

    code = sys.argv[1]
    user_input = sys.argv[2]

    # Save code to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as code_file:
        code_file.write(code.encode())
        code_file.flush()
        code_filename = code_file.name

    try:
        # Run user code with /usr/bin/time to measure resources
        result = subprocess.run(
            ["/usr/bin/time", "-f", "USED_TIME=%U;SYS_TIME=%S;ELAPSED=%E;MEM_KB=%M", "python3", code_filename],
            input=user_input,
            text=True,
            capture_output=True,
            timeout=5
        )

        program_output = result.stdout
        resource_info_line = result.stderr.strip().splitlines()[-1]

        usage = {}
        for part in resource_info_line.split(";"):
            if "=" in part:
                key, val = part.split("=")
                usage[key] = val

        print(json.dumps({
            "output": program_output.strip(),
            "exit_code": result.returncode,
            "resources": usage
        }))

    except subprocess.TimeoutExpired:
        print(json.dumps({"error": "Time Limit Exceeded"}))

    finally:
        os.remove(code_filename)

if __name__ == "__main__":
    main()
