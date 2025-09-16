from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import subprocess

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/run", methods=["POST"])
def run_code():
    data = request.json
    if not data or "code" not in data:
        return jsonify({"error": "No code provided"}), 400

    try:
        # Call runner.js.py (Python wrapper that executes Node.js code safely)
        process = subprocess.run(
            ["python3", "runner.js.py"],   # <-- changed here
            input=json.dumps(data),
            text=True,
            capture_output=True,
            timeout=5
        )

        if process.returncode != 0 and not process.stdout:
            return jsonify({"error": process.stderr.strip()}), 500

        return jsonify(json.loads(process.stdout.strip()))
    except subprocess.TimeoutExpired:
        return jsonify({
            "output": "",
            "error": "Time Limit Exceeded",
            "exit_code": -1,
            "resources": {}
        }), 408
    except Exception as e:
        return jsonify({
            "output": "",
            "error": str(e),
            "exit_code": -1,
            "resources": {}
        }), 500

@app.route("/", methods=["GET"])
def index():
    return "JS Code Execution API with runner.js.py is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
