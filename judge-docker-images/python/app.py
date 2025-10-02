from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/run", methods=["POST"])
def run_code():
    print("Python code is running...")

    data = request.get_json()
    if not data:
        return jsonify({"error": "No code provided"}), 400

    try:
        # Pass JSON to runner.py via stdin
        result = subprocess.run(
            ["python3", "runner.py"],
            input=json.dumps(data),
            text=True,
            capture_output=True,
            timeout=10
        )

        # Parse runner output
        output_json = json.loads(result.stdout.strip())
        return jsonify(output_json)

    except subprocess.TimeoutExpired:
        return jsonify({"output": "", "error": "Time Limit Exceeded", "exit_code": -1, "resources": {}}), 408
    except Exception as e:
        return jsonify({"output": "", "error": f"Execution Error: {str(e)}", "exit_code": -1, "resources": {}}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
