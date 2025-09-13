import sys, tempfile, subprocess, os, json

def main():
    # Read JSON from stdin: {"code": "...", "input": "..."}
    data = json.load(sys.stdin)
    print(data)
    code = data.get("code", "")
    user_input = data.get("input", "")

    # Save code to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as code_file:
        code_file.write(code.encode())
        code_file.flush()
        code_filename = code_file.name

    # Save user input to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as input_file:
        input_file.write(user_input.encode())
        input_file.flush()
        input_filename = input_file.name

    try:
        # Run the code via /usr/bin/time, feed input from file
        result = subprocess.run(
            ["/usr/bin/time", "-f", "USED_TIME=%U;SYS_TIME=%S;ELAPSED=%E;MEM_KB=%M", "python3", code_filename],
            stdin=open(input_filename, "r"),
            capture_output=True,
            text=True,
            timeout=5
        )

        # Separate stdout (program output) and stderr (time info)
        program_output = result.stdout
        resource_info_line = result.stderr.strip().splitlines()[-1]  # last line should have USED_TIME;SYS_TIME...

        usage = {}
        for part in resource_info_line.split(";"):
            if "=" in part:
                key, val = part.split("=")
                usage[key] = val

        # Print program output first, then usage JSON
        print(program_output, end="")
        print(json.dumps(usage))

    except subprocess.TimeoutExpired:
        print("Time Limit Exceeded")

    finally:
        os.remove(code_filename)
        os.remove(input_filename)

if __name__ == "__main__":
    main()
