import sys, tempfile, subprocess, os, json

def main():
    # Read C++ code from stdin
    data = json.load(sys.stdin)
    code = data.get("code", "")
    user_input = data.get("input", "")

    # Save code to temporary .cpp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".cpp") as code_file:
        code_file.write(code.encode())
        code_file.flush()
        code_filename = code_file.name
    
    # Save user input to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as input_file:
        input_file.write(user_input.encode())
        input_file.flush()
        input_filename = input_file.name

    try:
        # Compile
        exe_file = tempfile.NamedTemporaryFile(delete=False).name
        
        compile_result = subprocess.run(
            ["g++", code_filename, "-o", exe_file],
            capture_output=True,
            text=True
        )

        if compile_result.returncode != 0:
            # Compilation error
            output = compile_result.stderr
            usage = {}
        else:
            # Run with time & input
            run_result = subprocess.run(
                ["/usr/bin/time", "-f", "USED_TIME=%U;SYS_TIME=%S;ELAPSED=%E;MEM_KB=%M", exe_file],
                stdin=open(input_filename, "r"),
                capture_output=True,
                text=True,
                timeout=5
            )

            output = run_result.stdout
            resource_line = run_result.stderr.strip().splitlines()[-1]  # last line should have USED_TIME;SYS_TIME...
            usage = {}

            for part in resource_line.split(";"):
                if "=" in part:
                    key, val = part.split("=")
                    usage[key] = val
            
        # Return JSON
        print(json.dumps({"output": output, "usage": usage}))

    except subprocess.TimeoutExpired:
        print(json.dumps({"error": "Time Limit Exceeded", "output": "", "usage": {}}))
    
    finally:
        os.remove(code_filename)
        os.remove(input_filename)
        if os.path.exists(exe_file):
            os.remove(exe_file)

if __name__ == "__main__":
    main()
