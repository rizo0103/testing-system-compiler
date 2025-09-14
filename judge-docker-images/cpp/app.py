import sys, subprocess, tempfile, os, json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/run', methods=['POST'])
def run_code():
    try:
        data = request.get_json()
        code = data.get("code", "")
        user_input = data.get("input", "")

        # Save code to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cpp") as code_file:
            code_file.write(code.encode())
            code_file.flush()
            code_filename = code_file.name

        # Save input to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as input_file:
            input_file.write(user_input.encode())
            input_file.flush()
            input_filename = input_file.name

        exe_file = code_filename.replace(".cpp", "")

        # Compile code
        compile_process = subprocess.run(
            ["g++", code_filename, "-o", exe_file],
            capture_output=True,
            text=True
        )

        if compile_process.returncode != 0:
            return jsonify({
                "output": "",
                "error": compile_process.stderr.strip(),
                "exit_code": compile_process.returncode,
                "resources": {}
            })

        # Run executable with resource measurement
        result = subprocess.run(
            ["/usr/bin/time", "-f", "USED_TIME=%U;SYS_TIME=%S;ELAPSED=%E;MEM_KB=%M", exe_file],
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

        return jsonify({
            "output": program_output,
            "error": None if result.returncode == 0 else result.stderr.strip(),
            "exit_code": result.returncode,
            "resources": resources
        })

    except subprocess.TimeoutExpired:
        return jsonify({
            "output": "",
            "error": "Time Limit Exceeded",
            "exit_code": -1,
            "resources": {}
        })
    finally:
        if os.path.exists(code_filename): os.remove(code_filename)
        if os.path.exists(input_filename): os.remove(input_filename)
        if os.path.exists(exe_file): os.remove(exe_file)

@app.route("/", methods=["GET"])
def home():
    return "C++ Code Runner is alive 🚀"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)