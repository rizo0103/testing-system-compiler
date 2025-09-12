import sys, tempfile, subprocess, os

def main():
    # Read code from stdin
    code = sys.stdin.read()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".js") as tmp:
        tmp.write(code.encode())
        tmp.flush()
        filename = tmp.name
    
    try:
        result = subprocess.run(
            ["node", filename],
            capture_output=True,
            text=True,
            timeout=5  # 5 seconds time limit
        )

        print(result.stdout)

        if result.stderr:
            print(result.stderr)
    
    except subprocess.TimeoutExpired:
        print("Time Limit Exceeded")
    
    finally:
        os.remove(filename)

if __name__ == "__main__":
    main()    