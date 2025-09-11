import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/run/python", methods=["POST"])
def run_python():
    code = request.json.get("code", "")
    if not code:
        return jsonify({"error": "No code provided"}), 400

    try:
        # Run docker container and pass code via stdin
        result = subprocess.run(
            ["docker", "run", "-i", "--rm", "code-runner-python"],
            input=code,
            text=True,
            capture_output=True,
            timeout=10  # safety timeout in seconds
        )
        return jsonify({
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exitCode": result.returncode
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Time Limit Exceeded"}), 408
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def index():
    return "Code Execution API is running."

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
