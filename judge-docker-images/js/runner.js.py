import sys, tempfile, subprocess, os, json, platform

def main():
    data = json.load(sys.stdin)
    code = data.get("code", "")
    user_input = data.get("input", "")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".js") as code_file:
        code_file.write(code.encode())
        code_file.flush()
        code_filename = code_file.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as input_file:
        input_file.write(user_input.encode())
        input_file.flush()
        input_filename = input_file.name

    try:
        # Pick correct command depending on OS
        if platform.system() == "Linux":
            cmd = ["/usr/bin/time", "-f",
                   "USED_TIME=%U;SYS_TIME=%S;ELAPSED=%E;MEM_KB=%M",
                   "node", code_filename]
        else:  # Windows/Mac fallback
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

        output = {
            "output": program_output,
            "error": "\n".join(stderr_lines) if stderr_lines else None,
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
        try:
            os.remove(code_filename)
        except: pass
        try:
            os.remove(input_filename)
        except: pass

if __name__ == "__main__":
    main()
