import sys, tempfile, subprocess, os

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
            ["python3", filename],
            capture_output=True,
            text=True,
            timeout=5 # Safetu timeout in seconds
        )

        # Print stdout + strerr
        print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="")
        
    except subprocess.TimeoutExpired:
        print("Time Limit Exceeded")
    
    finally:
        os.remove(filename)
    
if __name__ == "__main__":
    main()