import sys, tempfile, subprocess, os

def main():
    code = sys.stdin.read()

    # Save code to temporary .cpp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".cpp") as tmp:
        tmp.write(code.encode())
        tmp.flush()
        filename = tmp.name
    
    executable = filename + ".out"
    try:
        # Compile the C++ code
        compile_result = subprocess.run(
            ["g++", filename, "-o", executable],
            capture_output=True,
            text=True,
            timeout=5  # Compilation timeout
        )

        if compile_result.returncode != 0:
            print(compile_result.stderr, end="")
            
            return

        # Run the compiled executable
        run_result = subprocess.run(
            [executable],
            capture_output=True,
            text=True,
            timeout=5  # Execution timeout
        )

        print(run_result.stdout, end="")

        if run_result.stderr:
            print(run_result.stderr, end="")

    except subprocess.TimeoutExpired:
        print("Time Limit Exceeded")
    
    finally:
        os.remove(filename)
        if os.path.exists(executable):
            os.remove(executable)

if __name__ == "__main__":
    main()
