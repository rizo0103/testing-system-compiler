import sys, tempfile, subprocess, os, json

def main():
    # Read code from stdin
    code = sys.stdin.read()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
        tmp.write(code.encode())
        tmp.flush()
        filename = tmp.name
    
    try:
        # Run the code with a subprocess
        result = subprocess.run(
            ["/usr/bin/time", "-f", "USED_TIME=%U;SYS_TIME=%S;ELAPSED=%E;MEM_KB=%M", "python3", filename],
            capture_output=True,
            text=True,
            timeout=5 # Safetu timeout in seconds
        )

        # Separate program output (stdout) and resource usage (stderr)
        program_output = result.stdout
        resource_lines = result.stderr.strip().split("\n")

        # Extract resource usage from last line
        usage = {}
        if resource_lines:
            for part in resource_lines[-1].split(";"):
                key, val = part.split("=")
                usage[key] = val
            
        # Print program output first
        print(program_output, end="")

        # Then print JSON usage stats
        print(json.dumps(usage))

    except subprocess.TimeoutExpired:
        print("Time Limit Exceeded")
    
    finally:
        os.remove(filename)
    
if __name__ == "__main__":
    main()